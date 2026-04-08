---
title: E-commerce Inventory Manager Env
emoji: 📦
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - reinforcement-learning
---

# E-commerce Inventory Manager Environment

An OpenEnv RL environment simulating a real-world backend inventory management system. It provides a structured interface for an AI agent to monitor stock levels, respond to supply chain issues, and adjust pricing.

## Environment Description
The agent acts as an automated inventory manager. The underlying state is a hidden dictionary representing a real-time database of products, their current stock, and their prices. The agent must interact with this system to solve specific business tasks (like ordering stock or fighting inflation) through a discrete API.

### The 3 Tasks
1. **Task 1 (Easy) - Restock:** The agent must order exactly 50 units of a depleted item (SKU-101).
2. **Task 2 (Medium) - Price Adjustment:** The agent must adjust the price of an item (SKU-102) to combat inflation, requiring it to check current prices first.
3. **Task 3 (Hard) - Full Audit:** The agent must identify multiple items with low stock (< 10) and calculate the exact order quantity needed to bring their stock levels to precisely 100 units.

---

## The OpenEnv API

### Action Space (`InventoryAction`)
The agent can output three discrete actions by returning a JSON object matching this schema:
* `action_type` (str): Must be one of `check_inventory`, `order_stock`, or `update_price`.
* `sku` (str, optional): The product identifier (e.g., "SKU-101").
* `quantity` (int, optional): The number of units to order.
* `price` (float, optional): The new price to set.

### Observation Space (`InventoryObservation`)
The environment returns text-based observations mapping partial progress, task completion, or error states.
* `echoed_message` (str): Feedback detailing the result of the previous action or current task requirements.
* `inventory_data` (dict, optional): JSON representation of the database, only visible when `check_inventory` is called.

### Reward Function
The reward function is deterministic and clamped between `0.0` and `1.0`. 
* The agent receives partial rewards (e.g., `0.3`) for gathering necessary information (like calling `check_inventory` on complex tasks) or partially completing a multi-step restock.
* The agent receives a `1.0` reward upon the exact completion of the active task's goal.

---

## Setup & Execution Instructions

### 1. Local Setup
Ensure you have the required dependencies installed:
```bash
pip install -r requirements.txt