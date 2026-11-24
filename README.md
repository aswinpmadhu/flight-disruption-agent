# AI Flight Disruption Recovery Agent

An AI-powered flight disruption recovery assistant that helps passengers understand flight disruptions, explore alternative itineraries, and request rebooking through a controlled, approval-based workflow.

Built using **Python, FastAPI, and Anthropic Claude**, this project demonstrates how agentic AI can support airline post-booking operations.

> **Project status:** In development  
> **Data:** Synthetic airline and passenger data only  
> **Purpose:** Hackathon demonstration and learning project

---

## 1. Problem Statement

Flight disruptions such as cancellations, delays, and missed connections create a frustrating experience for passengers.

Passengers often need to:
- Understand what happened to their flight.
- Check applicable airline policies.
- Find suitable alternative itineraries.
- Understand their available recovery options.
- Confirm a rebooking request.

This project explores how an AI agent can simplify that experience by combining LLM reasoning, tool calling, retrieval-augmented generation (RAG), and human approval.

## 2. Solution Overview

The AI agent acts as a conversational flight disruption recovery assistant.

A passenger describes their disruption, and the agent follows a controlled workflow:

1. Retrieve the passenger's synthetic booking details
