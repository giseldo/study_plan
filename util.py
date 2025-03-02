from crewai import Task, LLM, Agent, Crew
from xhtml2pdf import pisa
import markdown
import io
import os
import tempfile
import hashlib

# Password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def markdown_to_pdf(markdown_text):
    """
    Convert markdown text to PDF content
    """
    # Convert markdown to HTML
    html_text = markdown.markdown(markdown_text)
    
    # Add some basic styling
    styled_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #3498db; }}
            h3 {{ color: #2980b9; }}
            a {{ color: #3498db; }}
        </style>
    </head>
    <body>
        {html_text}
    </body>
    </html>
    """
    
    # Create PDF from HTML content
    pdf_output = io.BytesIO()
    pisa.CreatePDF(styled_html, dest=pdf_output)
    pdf_output.seek(0)
    
    return pdf_output

def executar_equipe_interface(disciplina, assunto, topicos_str):

    groqllm = LLM(model="groq/llama-3.3-70b-versatile")

    # Converter a string de tópicos para uma lista
    topicos = [t.strip() for t in topicos_str.split(',') if t.strip()]
    
    solicitacao = {
        "disciplina": disciplina,
        "assunto": assunto,
        "topicos": topicos
    }

    disciplina = solicitacao['disciplina']
    assunto = solicitacao['assunto']
    topicos = ', '.join(solicitacao['topicos'])

    agentMotivador = Agent(
        role='Motivador',
        goal='Escrever uma mensagem motivacional para o estudante.',
        backstory='Você é um coach motivacional com experiência em ajudar estudantes a manterem o foco.',
        llm=groqllm
    )

    agentPlano = Agent(
        role='Coordenador de Estudos',
        goal=f'Sua tarefa é criar um plano de estudo estruturado com base nas seguintes informações: Disciplina: {disciplina}, Assunto: {assunto}, Tópicos: {topicos}',
        backstory='Você é um especialista em educação com experiência em criar planos de estudos eficientes.',
        llm=groqllm
    )

    agentMaterialVideo = Agent(
        role='Pesquisador de Material',
        goal=f'Sua tarefa é pesquisar no Youtube por vídeos que explique as Disciplina: {disciplina} sobre o Assunto: {assunto} e seus Tópicos: {topicos}',
        backstory='Você é um especialista em educação com experiência em criar planos de estudos eficientes.',
        llm=groqllm
    )

    tarefaMotivar =  Task(
        description='Escrever uma mensagem motivacional para o estudante.',
        agent=agentMotivador,
        expected_output='Dois parágrafos com uma Mensagem motivacional em markdown.',
    )

    tarefaGerarPlano = Task(
        description=f'Criar um plano de estudo estruturado com base nas seguintes informações: Disciplina: {disciplina}, Assunto: {assunto}, Tópicos: {topicos}.',
        agent=agentPlano,
        expected_output='Plano de estudos personalizado em markdown',
    )

    tarefaBuscarVideos = Task(
        description=f'Pesquisar no Youtube por vídeos que explique as Disciplina: {disciplina} sobre o Assunto: {assunto} e seus Tópicos: {topicos}',
        agent=agentMaterialVideo,
        expected_output='Lista de vídeos relacionados ao assunto em markdown.',
    )

    saida1 = agentMotivador.execute_task(tarefaMotivar)
    saida2 = agentPlano.execute_task(tarefaGerarPlano)
    saida3 = agentMaterialVideo.execute_task(tarefaBuscarVideos)

    saida_final = f"{saida1}\n\n{saida2}\n\n{saida3}"
    
    # Generate PDF from the output
    pdf_output = markdown_to_pdf(saida_final)
    
    # Save the PDF to a temporary file
    temp_dir = tempfile.gettempdir()
    pdf_filename = f"material_estudo_{hash_password(saida_final)[:8]}.pdf"
    pdf_path = os.path.join(temp_dir, pdf_filename)
    
    with open(pdf_path, 'wb') as f:
        f.write(pdf_output.getbuffer())
    
    return saida_final, pdf_path