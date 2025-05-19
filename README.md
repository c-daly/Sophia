# Sophia:A Modular AI Agent

Sophia is a conversational AI agent designed to be modular, extensible, and capable of sophisticated interactions through natural language, memory, and tool usage. This project explores how multiple systems—including LLMs, vector databases, and knowledge graphs—can be combined into a coherent architecture suitable for both experimentation and deployment.

---

## Features

* **Conversational Intelligence**: Uses HuggingFace and OpenAI APIs for language modeling.
* **Long-Term Memory**: Stores semantic representations of interactions and context using Milvus vector DB.
* **Knowledge Integration**: Leverages a Neo4j knowledge graph to store structured, interrelated concepts.
* **Tool Use**: Plans and executes API calls or internal functions in response to user requests.
* **Modular Architecture**: Designed to support swapping models, databases, or execution tools easily.

---

## Architecture Overview

Sophia is composed of the following core modules:

* **LLM Interface**: Abstract layer for querying LLMs (HuggingFace or OpenAI)
* **Memory Store**: Vector storage and retrieval layer using Milvus
* **Knowledge Graph**: Semantic web of concepts powered by Neo4j
* **Tool Executor**: Interface to trigger external functions or API tools
* **Conversation Engine**: Core logic that orchestrates dialog flow and context management

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Defiant-Duck/Sophia.git
cd Sophia
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file and populate it with the following keys:

```env
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_API_KEY=your_hf_key
MILVUS_HOST=localhost
MILVUS_PORT=19530
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

## Future Plans

* Integration with voice interfaces
* More advanced tool selection logic
* Plugin interface for adding new skills
* Visualization dashboards for memory and knowledge graph

---

## Contributing

Contributions are welcome! Feel free to fork this repo, submit PRs, or open issues.

---

## License

MIT License

---

## Contact

Created by [Christopher D. Daly](https://github.com/c-daly). For questions or feedback, feel free to reach out via [email](mailto:chris@cdaly.me).
 
