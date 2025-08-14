# Spenderella Backend

Backend of Spenderella, a full-stack expense tracker automating financial data aggregation and categorization.

## Overview
- FastAPI REST API with PostgreSQL and SQLAlchemy ORM  
- Plaid API integration with secure Fernet-encrypted token storage  
- Webhook-based incremental transaction synchronization  
- Atomic CRUD operations for categories and transactions  
- Database schema with foreign key constraints and cascading deletes

## Tech Stack
- **Backend:** Python, FastAPI  
- **Database:** PostgreSQL, SQLAlchemy ORM  
- **Security:** Fernet encryption, token management  
- **Integration:** Plaid API, Webhooks

## Features
- Modular, RESTful API design for scalable endpoints  
- Transaction syncing with event-driven webhooks  
- Secure storage and retrieval of sensitive financial data  
- High-performance database queries and normalized schema
