from mcp.services.plan_and_execute_client import PlanAndExecuteClient

def main():
    client = PlanAndExecuteClient()

    print("Ask anything related to document processing. Example:")
    print("   merge all documents from Azure Blob and generate a Word document.\n")

    while True:
        command = input("You: ")
        if command.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break

        try:
            result = client.send_command(command)
            print("Agent response:")
            print(result)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()
