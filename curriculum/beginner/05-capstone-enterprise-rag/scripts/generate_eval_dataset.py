import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Note: In the Capstone, the golden evaluation dataset is pre-generated in data/evaluation/.
# This script is provided as a reference to demonstrate how synthetic evaluation datasets
# can be generated programmatically using an LLM to scale evaluation set creation.

def generate_qa_pairs(document_text: str, category: str, count: int = 2) -> str:
    """Uses an LLM to generate synthetic QA pairs based on a document."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    
    prompt = ChatPromptTemplate.from_template(
        "You are an expert curriculum developer. Based on the following document text, "
        "generate {count} QA pairs of category '{category}'.\\n\\n"
        "Document Text:\\n{document_text}\\n\\n"
        "Output the result as a JSON list containing objects with keys: "
        "'question', 'expected_answer', 'answerable' (boolean), 'difficulty' (easy/medium/hard).\\n"
        "Make sure to strictly format it as JSON without markdown wrappers if possible."
    )
    
    chain = prompt | llm
    response = chain.invoke({
        "document_text": document_text,
        "category": category,
        "count": count
    })
    
    return response.content

def main():
    print("This is a demonstration script. The actual golden dataset is pre-generated in data/evaluation/golden_dataset.json.")
    print("To regenerate, uncomment the generation code in this script.")
    
    # Example usage:
    # doc_text = "Employees receive up to 16 weeks of fully paid parental leave."
    # qa_json = generate_qa_pairs(document_text=doc_text, category="single_source", count=1)
    # print(qa_json)

if __name__ == "__main__":
    main()
