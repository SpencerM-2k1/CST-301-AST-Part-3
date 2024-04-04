from g4f.client import Client

client = Client()

# Uses `message.py` by Dylan Johnson as template

messages = [
    {"role": "system",
     "content": "You are attempting to classify the inputted description into one of the 31 labels based off of the similarity to it."},
    # {"role": "system",
    #  "content": "As you guess this, your final response should only be in bullet points."},
    {"role": "system",
     "content": "Answer in the format of: Label: given label of this description"
                                        "Reason: reason why this label was chosen"}
]
options = {
    "Application": "third party apps or plugins for specific use attached to the system",
    "Application Performance Manager": "monitors performance or benchmark",
    "Big Data": "API's that deal with storing large amounts of data. with variety of formats",
    "Cloud": "APUs for software and services that run on the Internet",
    "Computer Graphics": "Manipulating visual content",
    "Data Structure": "Data structures patterns (e.g., collections, lists, trees)",
    "Databases": "Databases or metadata",
    "Software Development and IT": "Libraries for version control, continuous integration and continuous delivery",
    "Error Handling": "response and recovery procedures from error conditions",
    "Event Handling": "answers to event like listeners",
    "Geographic Information System": "Geographically referenced information",
    "Input/Output": "read, write data",
    "Interpreter": "compiler or interpreter features",
    "Internationalization": "integrate and infuse international, intercultural, and global dimensions",
    "Logic": "frameworks, patterns like commands, controls, or architecture-oriented classes",
    "Language": "internal language features and conversions",
    "Logging": "log registry for the app",
    "Machine Learning": "ML support like build a model based on training data",
    "Microservices/Services": "Independently deployable smaller services. Interface between two different applications so that they can communicate with each other",
    "Multimedia": "Representation of information with text, audio, video",
    "Multithread": "Support for concurrent execution",
    "Natural Language Processing": "Process and analyze natural language data",
    "Network": "Web protocols, sockets RMI APIs",
    "Operating System": "APIs to access and manage a computer's resources",
    "Parser": "Breaks down data into recognized pieces for further analysis",
    "Search": "API for web searching",
    "Security": "Crypto and secure protocols",
    "Setup": "Internal app configurations",
    "User Interface": "Defines forms, screens, visual controls",
    "Utility": "third party libraries for general use",
    "Test": "test automation"
}

def getTags(classDescription, requestFor):
    if "was not found within the documentation (might be inherited)." in classDescription:
        classDescription = requestFor

    print("Requesting tags for " + requestFor + "...")

    # Construct the prompt with the object description and option descriptions
    prompt = "Does this class description: "
    prompt += f"Object Description: {classDescription}\n"
    prompt += " more fit with which of these options: "
    prompt += f"Options: {options}\n"
    prompt += "Only include bullet points in your answer. Discard any part of the response which is not a bullet point.\n"
    prompt += "Place a line break between the label and reason for each bullet point.\n"
    prompt += "Format the name of the label like this: Label<`NameOfLabel`>:"
    # prompt += "Do not include a blank line break separate bullet points.\n"
    # prompt += "Only include the most relevant option, and discard the rest.\n"
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        stream=True
    )
    return response