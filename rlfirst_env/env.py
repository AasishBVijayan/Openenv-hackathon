from models import InventoryAction, InventoryObservation, EnvResult

class InventoryEnv:
    def __init__(self):
        self.inventory = {}
        self.steps_taken = 0
        self.max_steps = 15
        self.active_task = 0
        
        # Define our 3 tasks (Easy, Medium, Hard)
        self.task_prompts = {
            1: "Task 1 (Easy): We are out of Wireless Mice (SKU-101). Please order 50 units.",
            2: "Task 2 (Medium): Inflation is hitting us. Increase the price of Mechanical Keyboards (SKU-102) by $10.",
            3: "Task 3 (Hard): Run an audit. Find any item with less than 10 units in stock, and order enough to bring their stock exactly up to 100 units."
        }

    async def reset(self) -> EnvResult:
        """Resets the environment and cycles to the next task."""
        self.steps_taken = 0
        
        # Cycle through tasks 1, 2, and 3 on each reset
        self.active_task = self.active_task + 1 if self.active_task < 3 else 1
        
        # Initial State
        self.inventory = {
            "SKU-101": {"name": "Wireless Mouse", "stock": 0, "price": 25.0},
            "SKU-102": {"name": "Mechanical Keyboard", "stock": 50, "price": 100.0},
            "SKU-103": {"name": "USB-C Cable", "stock": 5, "price": 15.0},
        }
        
        obs = InventoryObservation(
            echoed_message=f"System initialized. {self.task_prompts[self.active_task]}",
            inventory_data=None # Hide inventory initially
        )
        return EnvResult(observation=obs, reward=0.0, done=False)

    async def state(self) -> dict:
        """Returns the hidden state for the evaluator."""
        return {"inventory": self.inventory, "steps": self.steps_taken, "active_task": self.active_task}

    async def step(self, action: InventoryAction) -> EnvResult:
        """Processes the action, updates the state, and calculates the reward."""
        self.steps_taken += 1
        reward = 0.0
        done = False
        message = ""

        # --- 1. PROCESS THE ACTION ---
        if action.action_type == "check_inventory":
            message = "Inventory checked successfully."
            # Partial reward for gathering info on Medium/Hard tasks
            if self.active_task in [2, 3]:
                reward = 0.3 
                
        elif action.action_type == "order_stock":
            if action.sku in self.inventory and action.quantity is not None:
                self.inventory[action.sku]["stock"] += action.quantity
                message = f"Ordered {action.quantity} units of {action.sku}."
            else:
                message = "Error: Invalid SKU or missing quantity."
                
        elif action.action_type == "update_price":
            if action.sku in self.inventory and action.price is not None:
                self.inventory[action.sku]["price"] = action.price
                message = f"Updated price of {action.sku} to ${action.price}."
            else:
                message = "Error: Invalid SKU or missing price."
        else:
            message = f"Error: Unknown action '{action.action_type}'."

        # --- 2. EVALUATE TASK SUCCESS (THE GRADERS) ---
        
        # Grader for Task 1 (Order 50 units of SKU-101)
        if self.active_task == 1:
            if action.action_type == "order_stock" and action.sku == "SKU-101":
                if action.quantity == 50:
                    reward = 1.0
                    done = True
                    message += " Task 1 Complete!"
                else:
                    reward = 0.5 
                    message += " Ordered stock, but wrong amount."

        # Grader for Task 2 (Increase SKU-102 price by $10 from base 100.0)
        elif self.active_task == 2:
            if action.action_type == "update_price" and action.sku == "SKU-102":
                if action.price == 110.0:
                    reward = 1.0
                    done = True
                    message += " Task 2 Complete!"
                else:
                    reward = 0.5
                    message += " Updated price, but wrong amount."

        # Grader for Task 3 (Audit and restock items < 10 up to 100)
        elif self.active_task == 3:
            s101 = self.inventory["SKU-101"]["stock"]
            s103 = self.inventory["SKU-103"]["stock"]
            
            if action.action_type == "order_stock":
                # Both low-stock items reached exactly 100
                if s101 == 100 and s103 == 100:
                    reward = 1.0
                    done = True
                    message += " Task 3 Complete!"
                # Partial progress: one item was restocked correctly
                elif s101 == 100 or s103 == 100:
                    reward = 0.7 
                    message += " Partial restock completed."

        # --- 3. TIMEOUT CHECK ---
        if self.steps_taken >= self.max_steps and not done:
            done = True
            message += " Max steps reached. Task failed."

        # Return the final observation
        obs = InventoryObservation(
            echoed_message=message,
            inventory_data=self.inventory if action.action_type == "check_inventory" else None
        )
        
        return EnvResult(observation=obs, reward=reward, done=done)