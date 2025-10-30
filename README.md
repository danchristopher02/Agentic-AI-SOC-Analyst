# 🤖 Agentic AI SOC Analyst

This project demonstrates an Agentic AI Security Operations Center (SOC) Analyst, designed to:

- Ingest and analyze logs

- Identify and score potential threats

- Recommend containment actions

- Generate professional SOC investigation reports

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
## 2. Builds KQL Query

Using OpenAI API, the agent builds a KQL query that will get the information to best answer the prompt. The agent displays the table and fields it will use, its rationale for choosing them, and the KQL query itself. Guardrails are put in place to make sure the agent does not use an unwanted table/field.

## 3. Logs are collected from the Log Analytics Workspace in Azure.

## 4. Builds USER Prompt

The User Prompt is built by combining the original user request, table/field information, and logs.

## 5. Retrieves SYSTEM Prompt

The System Prompt is set in the code: 

## 6. Combines USER + SYSTEM Prompts

The User and System Prompts are combined into one prompt. The tokens are then calculated and the cost is estimated for different OpenAI models.

## 7. User decides Model

The user chooses which model to use. Guardrails are in place to make sure the calculated token amount is less than the token limit for that model.

## 8. Threat Hunt Executed
The agent analyzes logs and returns potential threats 
