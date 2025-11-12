import subprocess

class OllamaReact:
    def __init__(self, model="llama3.2:1b"):
        self.model = model
        # Make sure to update this path to yours
        self.ollama_path = r"C:\Users\GSPL\AppData\Local\Programs\Ollama\ollama.exe"

    def generate(self, prompt):
        try:
            result = subprocess.run(
                [self.ollama_path, "run", self.model],
                input=prompt,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",    
                errors="ignore"      
            )
            return result.stdout.strip()
        except Exception as e:
            print("Ollama error:", e)
            return None
          
