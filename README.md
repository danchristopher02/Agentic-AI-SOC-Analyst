# 🤖 Agentic AI SOC Analyst

This project demonstrates an Agentic AI Security Operations Center (SOC) Analyst, designed to:

- Ingest and analyze logs

- Identify and score potential threats

- Automatically Isolate affected hosts

## Things to Know Beforehand

### Azure VMs
A set of internet-facing Azure virtual machines are intentionally exposed to attract real-world malicious activity. These interactions generate security logs that the AI SOC Analyst Agent analyzes for threat detection and response.
Using the Azure API, the agent connects to and queries the log tables that store this data.


### OpenAI System and User Prompts
When interacting with the OpenAI API, both a System Prompt and a User Prompt are required:

- System Prompt: Establishes the AI’s context, tone, and behavior (e.g., “You are a SOC analyst.”).

- User Prompt: Represents the user’s direct query or task (e.g., “Analyze these security logs for anomalies.”).


### OpenAI Token System and Model Pricing
OpenAI models process text in units called tokens, which represent small chunks of text—typically about four characters. Both prompts (input) and responses (output) consume tokens.

Each OpenAI model has a maximum token limit (the total size of input + output it can handle) and a cost per token, which varies based on the model’s capability and performance.



# How the Agent Works

## 1. Prompts user for input. User then provides prompt/request.

<img width="824" height="78" alt="image" src="https://github.com/user-attachments/assets/c4d96d37-4128-471c-8c19-dcdf5032b013" />


## 2. Builds KQL Query

Using OpenAI API, the agent builds a KQL query that will get the information to best answer the prompt. The agent displays the table and fields it will use, its rationale for choosing them, and the KQL query itself. Guardrails are put in place to make sure the agent does not use an unwanted table/field.

<img width="1087" height="371" alt="image" src="https://github.com/user-attachments/assets/b21016fa-259d-4743-bfc6-fcc711223901" />



## 3. Logs are collected from the Log Analytics Workspace in Azure.

<img width="569" height="51" alt="image" src="https://github.com/user-attachments/assets/2682c9f9-3d73-4ff1-a32d-51afdc356a9e" />


## 4. Builds USER Prompt

The User Prompt is built by combining the original user request, table/field information, and logs.

## 5. Retrieves SYSTEM Prompt

The System Prompt is set in the code: 

## 6. Combines USER + SYSTEM Prompts

The User and System Prompts are combined into one prompt. The tokens are then calculated and the cost is estimated for different OpenAI models.

<img width="874" height="167" alt="image" src="https://github.com/user-attachments/assets/e91eb193-adf0-43dc-8d92-5fafb16c895b" />


## 7. User decides Model

The user chooses which model to use. Guardrails are in place to make sure the calculated token amount is less than the token limit for that model.

<img width="566" height="49" alt="image" src="https://github.com/user-attachments/assets/6217e905-a9c8-431b-921b-97d8f51f5dd3" />


## 8. Threat Hunt Executed
The agent analyzes logs and returns potential threats 

<img width="1092" height="766" alt="image" src="https://github.com/user-attachments/assets/eb886ee4-fde4-4d1c-a5b5-b03708405568" />

## 9. Threats are logged into a .json file

## 10. Agent isolates VM
For high confidence threats detected on the virtual machine, the user has the choice to have the agent isolate.

<img width="601" height="75" alt="image" src="https://github.com/user-attachments/assets/e1f265d8-3d6b-4a03-89c5-21df5a5ec9ec" />


