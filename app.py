# app.py
import gradio as gr
from utils import CSVHandler, PlotGenerator, SimpleAIAgent, QueryResponse
import tempfile
import pandas as pd

class App:
    def __init__(self):
        self.df = None
        self.agent = SimpleAIAgent()
        
    def handle_upload(self, file):
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                with open(file.name, "rb") as f:
                    content = f.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            self.df = CSVHandler.validate_csv(tmp_path)
            return f"CSV loaded with {len(self.df)} rows and {len(self.df.columns)} columns"
        except Exception as e:
            return f"Error: {str(e)}"

    def process_question(self, question):
        if self.df is None:
            return "Please upload a CSV file first", None
        
        try:
            response = self.agent.process_query(self.df, question)
            
            plot = None
            if response.plot_type and response.plot_columns:
                plot = PlotGenerator.generate_plot(
                    self.df,
                    response.plot_type,
                    response.plot_columns
                )
            
            return response.answer, plot
        except Exception as e:
            return f"Error processing query: {str(e)}", None

    def run(self):
        with gr.Blocks(title="CSV Analyzer") as demo:
            gr.Markdown("# CSV Data Analysis Assistant")
            
            with gr.Row():
                csv_upload = gr.File(label="Upload CSV", file_count="single")
                upload_status = gr.Textbox(label="Upload Status")
                
            with gr.Row():
                sample_csv = gr.File(label="Download Sample CSV", value="sample.csv")
            
            with gr.Row():
                question_input = gr.Textbox(label="Enter your question")
                submit_btn = gr.Button("Submit")
            
            with gr.Row():
                answer_output = gr.Textbox(label="Answer")
                plot_output = gr.Plot(label="Visualization")
            
            csv_upload.change(
                self.handle_upload,
                inputs=csv_upload,
                outputs=upload_status
            )
            
            submit_btn.click(
                self.process_question,
                inputs=question_input,
                outputs=[answer_output, plot_output]
            )
            
        demo.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    app = App()
    app.run()