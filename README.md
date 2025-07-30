# Smartphone Consultant
- Smartphone consultant is an AI-powered agent designed to enhance the online shopping experience by providing personalized product recommendations.
---

# Overview
This AI agent , **Smartphone Consultant** , is built on langGraph and aims to provide decisive shopping experience to all people using the power of LLM.It uses tavily for web search , and llama-3.1-70B-versatile model through groq. This ai agent is made using totally open source technologies.



---

# Motivation
This AI agent is made to assist a customer to get best desired product specifically tailoured for his needs and wants. Eventhough if do not has any expertise in that particular field of whose product he wants to buy, still using the power of **Smartphone Consultant** he could land for the best suited product for him.

---

# Key Features:
- **Tavily** for web search.
- **llama-3.3-70b-versatile** for arranging the data into specific schema and comparing products.
- Tells the best product among the searched ones.
- **Youtube API** for providing the review link of the best product for self-satisfaction.
- **SMTP** for sending mail about the best product and its review to the user.

## Directory Structure
```
├── src
│   ├── main.py
│   ├── nodes.py
│   ├── prompts.py
│   ├── utils.py
│   ├── config.py
│   └── models.py
├── requirements.txt
└── README.md
```

## Setup and run
- Set up API keys in your environment variables. (Create .env file and add your api keys)
- Run main.py with appropriate query and email inputs.
