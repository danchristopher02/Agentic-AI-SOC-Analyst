# --- imports and setup (keep these at the top) ---
import time
from colorama import Fore, init, Style
from openai import OpenAI
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
import UTILITIES
import _keys
import MODEL_MANAGEMENT
import PROMPT_MANAGEMENT
import EXECUTOR
import GUARDRAILS

# Initialize colorama once
init(autoreset=True)

# Build clients once (outside the loop)
law_client = LogsQueryClient(credential=DefaultAzureCredential())
openai_client = OpenAI(api_key=_keys.OPENAI_API_KEY)

# --- main program loop ---
while True:
    print(f"\n{Fore.LIGHTCYAN_EX}--- New Threat Hunt Session ---{Style.RESET_ALL}\n")
    
    # Assign the default model
    model = MODEL_MANAGEMENT.DEFAULT_MODEL

    # Get the message from the user
    user_message = PROMPT_MANAGEMENT.get_user_message()

    # Generate and sanitize query context
    unformatted_query_context = EXECUTOR.get_query_context(openai_client, user_message, model=model)
    query_context = UTILITIES.sanitize_query_context(unformatted_query_context)
    UTILITIES.display_query_context(query_context)

    # Validate tables and fields
    GUARDRAILS.validate_tables_and_fields(query_context["table_name"], query_context["fields"])

    # Query Log Analytics Workspace
    law_query_results = EXECUTOR.query_log_analytics(
        log_analytics_client=law_client,
        workspace_id=_keys.LOG_ANALYTICS_WORKSPACE_ID,
        timerange_hours=query_context["time_range_hours"],
        table_name=query_context["table_name"],
        device_name=query_context["device_name"],
        fields=query_context["fields"],
        caller=query_context["caller"],
        user_principal_name=query_context["user_principal_name"]
    )

    number_of_records = law_query_results['count']
    print(f"{Fore.WHITE}{number_of_records} record(s) returned.\n")

    if number_of_records == 0:
        print("No records found. Returning to main menu.")
        continue  # Skip to next iteration instead of exiting

    # Build the threat hunt prompt
    threat_hunt_user_message = PROMPT_MANAGEMENT.build_threat_hunt_prompt(
        user_prompt=user_message["content"],
        table_name=query_context["table_name"],
        log_data=law_query_results["records"]
    )

    threat_hunt_system_message = PROMPT_MANAGEMENT.SYSTEM_PROMPT_THREAT_HUNT
    threat_hunt_messages = [threat_hunt_system_message, threat_hunt_user_message]

    number_of_tokens = MODEL_MANAGEMENT.count_tokens(threat_hunt_messages, model)
    model = MODEL_MANAGEMENT.choose_model(model, number_of_tokens)
    GUARDRAILS.validate_model(model)

    print(f"{Fore.LIGHTGREEN_EX}Initiating cognitive threat hunt against targeted logs...\n")
    start_time = time.time()

    hunt_results = EXECUTOR.hunt(
        openai_client=openai_client,
        threat_hunt_system_message=PROMPT_MANAGEMENT.SYSTEM_PROMPT_THREAT_HUNT,
        threat_hunt_user_message=threat_hunt_user_message,
        openai_model=model
    )

    if not hunt_results:
        print("No hunt results found. Returning to main menu.")
        continue

    elapsed = time.time() - start_time
    print(f"{Fore.WHITE}Cognitive hunt complete. Took {elapsed:.2f} seconds and found {Fore.LIGHTRED_EX}{len(hunt_results['findings'])} {Fore.WHITE}potential threat(s)!\n")
    input(f"Press {Fore.LIGHTGREEN_EX}[Enter]{Fore.WHITE} to see results.")
    UTILITIES.display_threats(threat_list=hunt_results['findings'])

    token = EXECUTOR.get_bearer_token()
    machine_is_isolated = False

    for threat in hunt_results['findings']:
        threat_confidence_is_high = threat["confidence"].lower() == "high"
        query_is_about_individual_host = query_context["about_individual_host"]

        if query_is_about_individual_host and threat_confidence_is_high and not machine_is_isolated:
            print(Fore.YELLOW + "[!] High confidence threat detected on host:" + Style.RESET_ALL, query_context["device_name"])
            print(Fore.LIGHTRED_EX + threat['title'])
            confirm = input(f"{Fore.RED}{Style.BRIGHT}Would you like to isolate this VM? (yes/no): " + Style.RESET_ALL).strip().lower()
            
            if confirm.startswith("y"):
                machine_id = EXECUTOR.get_mde_workstation_id_from_name(token=token, device_name=query_context["device_name"])
                machine_is_isolated = EXECUTOR.quarantine_virtual_machine(token=token, machine_id=machine_id)
                if machine_is_isolated:
                    print(Fore.GREEN + "[+] VM successfully isolated." + Style.RESET_ALL)
                    print(Fore.CYAN + "Reminder: Release the VM from isolation when appropriate at: " + Style.RESET_ALL + "https://security.microsoft.com/")
            else:
                print(Fore.CYAN + "[i] Isolation skipped by user." + Style.RESET_ALL)

    # --- End of main logic; prompt for next action ---
    again = input(f"\n{Fore.LIGHTCYAN_EX}Would you like to perform another hunt? Type 'exit' to quit or press Enter to continue: {Style.RESET_ALL}").strip().lower()
    if again == "exit":
        print(f"{Fore.YELLOW}Exiting program. Goodbye!{Style.RESET_ALL}")
        break
