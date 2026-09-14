import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Note: In the Capstone, the corpus is pre-generated and provided in data/knowledge_base.
# This script is provided as a reference to demonstrate how a synthetic enterprise corpus 
# can be generated programmatically using an LLM.

def generate_policy(department: str, topic: str, instructions: str) -> str:
    """Uses an LLM to generate a synthetic enterprise policy document."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    
    prompt = ChatPromptTemplate.from_template(
        "You are a corporate communications writer for a fictional enterprise called Northstar Technologies.\\n"
        "Write a formal, realistic internal policy document for the {department} department.\\n"
        "Topic: {topic}\\n\\n"
        "Instructions:\\n{instructions}\\n\\n"
        "Format as Markdown. Include a title, effective date, version number, and clear headings.\\n"
        "Keep it concise but detailed enough to contain specific numbers, SLAs, or rules."
    )
    
    chain = prompt | llm
    response = chain.invoke({
        "department": department,
        "topic": topic,
        "instructions": instructions
    })
    
    return response.content

def main():
    print("This is a demonstration script. The actual corpus is pre-generated in data/knowledge_base.")
    print("To regenerate, uncomment the generation code in this script.")
    
    # Example usage:
    # doc_content = generate_policy(
    #     department="Engineering", 
    #     topic="Database Failover Runbook", 
    #     instructions="State that Tier 2 approval is required unless the cluster is completely unresponsive for >5 minutes, in which case Tier 1 can initiate."
    # )
    # print(doc_content)

if __name__ == "__main__":
    main()
