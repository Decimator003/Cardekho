# utils.py
import pandas as pd
import matplotlib.pyplot as plt
from pydantic import BaseModel
from typing import Optional
import logging
import requests

class CSVHandler:
    @staticmethod
    def validate_csv(file_path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                raise ValueError("CSV file is empty")
            return df
        except Exception as e:
            logging.error(f"CSV validation error: {e}")
            raise

class PlotGenerator:
    @staticmethod
    def generate_plot(df: pd.DataFrame, plot_type: str, columns: list) -> plt.Figure:
        plt.figure()
        try:
            if plot_type == 'scatter' and len(columns) == 2:
                df.plot.scatter(x=columns[0], y=columns[1])
            elif plot_type == 'line':
                df[columns].plot.line()
            elif plot_type == 'bar':
                df[columns].plot.bar()
            elif plot_type == 'hist':
                df[columns[0]].hist()
            else:
                raise ValueError(f"Unsupported plot type: {plot_type}")
            plt.tight_layout()
            return plt.gcf()
        except Exception as e:
            logging.error(f"Plot generation error: {e}")
            raise

class QueryResponse(BaseModel):
    answer: str
    plot_type: Optional[str] = None
    plot_columns: Optional[list] = None

class SimpleAIAgent:
    def __init__(self, model_name: str = "llama3:8b-instruct-q4_K_M"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434"
        self.verify_model()

    def verify_model(self):
        try:
            # Check if model exists
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": "test",
                    "stream": False
                }
            )
            if response.status_code != 200:
                print(f"Downloading model {self.model_name}...")
                requests.post(
                    f"{self.base_url}/api/pull",
                    json={"name": self.model_name}
                )
        except requests.ConnectionError:
            raise RuntimeError("Ollama server not running. Start it with 'ollama serve'")

    def process_query(self, df: pd.DataFrame, question: str) -> QueryResponse:
        columns = "\n".join(df.columns.tolist())
        sample_data = df.head(3).to_string()
        
        prompt = f"""Analyze this CSV data:
        
        Columns: {columns}
        Sample Data: {sample_data}
        
        Question: {question}
        
        Respond in JSON format with:
        - "answer": text response
        - "plot_type": optional plot type (scatter/line/bar/hist)
        - "plot_columns": list of columns for plotting
        """

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "format": "json",
                    "stream": False
                }
            )
            response.raise_for_status()
            json_response = response.json()
            return QueryResponse.parse_raw(json_response["response"])
        except Exception as e:
            return QueryResponse(answer=f"Error: {str(e)}")

# Test code
if __name__ == "__main__":
    agent = SimpleAIAgent()
    test_df = pd.DataFrame({
        "Price": [250000, 350000],
        "Area": [1500, 2000]
    })
    response = agent.process_query(test_df, "What is the average price?")
    print(response)