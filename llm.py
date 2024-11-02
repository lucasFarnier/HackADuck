import ollama
import random

class llm():
    def __init__(self, count):
        self.model = "llama2"
        self.format = '{"main": "main prompt", "1": "secondary", "2":"secondary",...}'
        self.count = count

    def get_theme(self, theme = "random"):
        theme = theme.lower()
        self.theme = ""
        if theme == "random":
            choice = random.randrange(3)
            if choice == 0:
                theme = "Halloween"
            elif choice == 1:
                theme = "Easter"
            elif choice == 2:
                theme = "Christmas"
            model = ollama.chat(
                model = self.model,
                messages=[{"role":"user", "content":f"Give me only one short 7 words drawing prompt on the theme {theme}"}],
                stream=True
            )
        else:
            model = ollama.chat(
                model = self.model,
                messages=[{"role":"user", "content":f"Give me only one short 7 words drawing prompt on the theme {theme}"}],
                stream=True
            )
        for chunk in model:
            self.theme+=chunk["message"]["content"]
        

    def get_keywords(self):
        self.get_theme()
        model = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": f"Give me main prompt and {self.count} key scene elements to draw based on the following drawing prompt {self.theme}. Please respond only in JSON format without any additional text, explanation, or pleasantries. Output the following data: {self.format} Ensure the response is valid JSON and strictly follows the specified structure. Do not include any extra information outside of this JSON format."}],
            stream=True
        )
        
        keywords = ""
        for chunk in model:
            keywords += chunk["message"]["content"]
        
        return keywords  # Return the keywords instead of printing
        
    def assign_prompts(self, player_count):
        keywords = self.get_keywords()
        # Assuming the response is valid JSON
        prompts_data = json.loads(keywords)

        # Create a list of secondary prompts for drawers
        main_prompt = prompts_data.get("main", "")
        secondary_prompts = {f"{i+1}": prompts_data.get(str(i+1), "") for i in range(player_count)}

        return main_prompt, secondary_prompts


        