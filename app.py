import gradio as gr
import util
import bd
import os

def main_app():
    # Load CSS from external file
    css_path = os.path.join(os.path.dirname(__file__), "static", "styles.css")
    try:
        with open(css_path, "r") as css_file:
            custom_css = css_file.read()
    except FileNotFoundError:
        # Fallback in case the file is not found
        print(f"Warning: CSS file not found at {css_path}")
        custom_css = ""
    
    with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as app:
        # Authentication state
        is_logged_in = gr.State(False)
        current_user = gr.State("")
        user_id = gr.State(None)  # Add state to store user ID
        full_data_state = gr.State([])  # Add state to store full study plan data

        # Login Interface
        with gr.Group(visible=True) as login_block:
            with gr.Column(elem_classes=["main-container"]):
                with gr.Row(elem_classes=["header"]):
                    gr.Markdown("# Sistema de Material de Estudo")
                    gr.Markdown("### Assistente Inteligente para Geração de Material Educacional")
                
                with gr.Column(elem_classes=["login-container"]):
                    gr.Markdown("### Login")
                    with gr.Group():
                        username_input = gr.Textbox(label="Usuário", placeholder="Digite seu nome de usuário")
                        password_input = gr.Textbox(label="Senha", type="password", placeholder="Digite sua senha")
                        login_message = gr.Textbox(label="", interactive=False, visible=False)
                        with gr.Row():
                            login_button = gr.Button("Entrar", variant="primary")
                    
                    with gr.Row(elem_classes=["register-link"]):
                        gr.Markdown("Não tem uma conta?")
                        register_nav_button = gr.Button("Cadastre-se", size="sm")
                        
                    with gr.Accordion("Informação", open=False):
                        gr.Markdown("""
                        Por favor insira suas credenciais para acessar o sistema.
                        """)
        
        # Registration Interface
        with gr.Group(visible=False) as register_block:
            with gr.Column(elem_classes=["main-container"]):
                with gr.Row(elem_classes=["header"]):
                    gr.Markdown("# Sistema de Material de Estudo")
                    gr.Markdown("### Cadastro de Novo Usuário")
                
                with gr.Column(elem_classes=["login-container"]):
                    with gr.Group():
                        new_username = gr.Textbox(label="Nome de Usuário", placeholder="Escolha um nome de usuário")
                        new_password = gr.Textbox(label="Senha", type="password", placeholder="Digite uma senha segura")
                        confirm_password = gr.Textbox(label="Confirmar Senha", type="password", placeholder="Digite a senha novamente")
                        register_message = gr.Textbox(label="", interactive=False, visible=False)
                        
                        with gr.Row():
                            back_button = gr.Button("Voltar", variant="secondary")
                            register_button = gr.Button("Cadastrar", variant="primary")
                    
                    with gr.Accordion("Informação", open=False):
                        gr.Markdown("""
                        Crie uma conta para acessar o sistema de geração de materiais de estudo.
                        """)

        # Main Application Interface
        with gr.Group(visible=False) as main_block:
            with gr.Column(elem_classes=["main-container"]):
                with gr.Row(elem_classes=["user-info"]):
                    user_display = gr.Markdown("Bem-vindo!")
                    logout_button = gr.Button("Sair", size="sm")
                
                gr.Markdown("# Gerador Inteligente de Material de Estudos")
                gr.Markdown("### Personalize seu material educacional completo em minutos")
                
                with gr.Column(elem_classes=["form-card"]):
                    gr.Markdown("### Dados do Material")
                    with gr.Row():
                        with gr.Column(scale=1):
                            disciplina_input = gr.Textbox(
                                label="Disciplina", 
                                placeholder="Ex: Matemática, Física, História...",
                                value="Matemática"
                            )
                        with gr.Column(scale=1):
                            assunto_input = gr.Textbox(
                                label="Assunto", 
                                placeholder="Ex: Funções, Leis de Newton, Segunda Guerra Mundial...",
                                value="Funções"
                            )
                    
                    topicos_input = gr.Textbox(
                        label="Tópicos (separados por vírgula)", 
                        placeholder="Ex: Função quadrática, Função exponencial, Função logarítmica...",
                        value="Função quadrática, Função exponencial, Função logarítmica",
                        lines=2
                    )
                
                with gr.Row():
                    generate_button = gr.Button("Gerar Material de Estudo", variant="primary", size="lg")

                
                # Output tabs
                with gr.Tabs() as tabs:
                    with gr.TabItem("Visualizar Material"):
                        markdown_output = gr.Markdown(label="Material Completo")
                    
                    with gr.TabItem("Download"):
                        with gr.Column():
                            gr.Markdown("### Download do Material")
                            pdf_output = gr.File(label="Download PDF")
                            gr.Markdown("Clique no botão acima para baixar seu material em formato PDF.")
                    
                    with gr.TabItem("Meus Materiais"):
                        with gr.Column():
                            gr.Markdown("### Meus Materiais de Estudo")
                            with gr.Row():
                                refresh_button = gr.Button("Atualizar Lista", size="sm")
                            
                            # Table to display user study plans - Fixed headers to match column count
                            materials_table = gr.Dataframe(
                                headers=["ID", "Título", "Data de Criação"],
                                datatype=["number", "str", "str"],
                                col_count=(3, "fixed"),
                                interactive=False,
                                wrap=True
                            )

        # Login function with improved feedback
        def login_fn(username, password):
            success, message, uid = bd.login(username, password)
            if success:
                # Get initial user study plans after login
                visible_plans, full_plans = load_study_plans(uid)
                
                return [
                    gr.update(visible=False),  # login_block
                    gr.update(visible=True),   # main_block
                    gr.update(value=message, visible=False),  # login_message
                    f"**Usuário:** {username}",  # user_display
                    True,  # is_logged_in
                    username,  # current_user
                    uid,  # user_id
                    visible_plans,  # materials_table
                    full_plans  # full_data for state
                ]
            else:
                return [
                    gr.update(visible=True),  # login_block
                    gr.update(visible=False),  # main_block
                    gr.update(value=message, visible=True),  # login_message
                    "",  # user_display
                    False,  # is_logged_in
                    "",  # current_user
                    None,  # user_id
                    [],  # materials_table
                    []  # full_data for state
                ]

        # Logout function
        def logout_fn():
            return [
                gr.update(visible=True),  # login_block
                gr.update(visible=False),  # main_block
                "",  # username_input
                "",  # password_input
                gr.update(value="", visible=False),  # login_message
                False,  # is_logged_in
                "",  # current_user
                None,  # user_id
                [],  # materials_table
                []  # full_data for state
            ]
        
        # Registration function
        def register_fn(username, password, confirm_password):
            success, message = bd.register_user(username, password, confirm_password)
            if success:
                # Return to login screen with success message
                return [
                    gr.update(visible=False),  # register_block
                    gr.update(visible=True),   # login_block
                    gr.update(value=message, visible=True),  # login_message
                    "",  # new_username
                    "",  # new_password
                    "",  # confirm_password
                    gr.update(value="", visible=False)  # register_message
                ]
            else:
                return [
                    gr.update(visible=True),  # register_block
                    gr.update(visible=False),  # login_block
                    gr.update(value="", visible=False),  # login_message
                    username,  # new_username (preserve input)
                    "",  # new_password
                    "",  # confirm_password
                    gr.update(value=message, visible=True)  # register_message
                ]
        
        # Navigation functions
        def show_register():
            return [
                gr.update(visible=False),  # login_block
                gr.update(visible=True),   # register_block
                gr.update(value="", visible=False)  # login_message
            ]
        
        def show_login():
            return [
                gr.update(visible=False),  # register_block
                gr.update(visible=True),   # login_block
                gr.update(value="", visible=False)  # register_message
            ]

        def generate_material(disciplina, assunto, topicos, user_id):
            
            # Execute the actual material generation
            markdown_output, pdf = util.executar_equipe_interface(disciplina, assunto, topicos)
            
            # Save the study plan to the database if user is logged in
            if user_id:
                success, plan_id = bd.save_study_plan(markdown_output, user_id)
                if success:
                    print(f"Successfully saved study plan with ID: {plan_id}")
                else:
                    print("Failed to save study plan to database")
            
            return [
                markdown_output,  # markdown_output
                pdf,  # pdf_output
            ]

        # Function to fetch and display user study plans
        def load_study_plans(user_id):
            if user_id:
                plans = bd.get_user_study_plans(user_id)
                # Return only the visible columns (ID, Title, Date)
                visible_data = [[row[0], row[1], row[2]] for row in plans]
                # Store full data in state for later use
                return visible_data, plans
            return [], []
        
        # Connect buttons to functions
        login_button.click(
            login_fn,
            inputs=[username_input, password_input],
            outputs=[login_block, main_block, login_message, user_display, is_logged_in, 
                    current_user, user_id, materials_table, full_data_state]
        )
        
        logout_button.click(
            logout_fn,
            outputs=[login_block, main_block, username_input, password_input, 
                     login_message, is_logged_in, current_user, user_id, materials_table, gr.State([])]
        )
        
        # Registration navigation buttons
        register_nav_button.click(
            show_register,
            outputs=[login_block, register_block, login_message]
        )
        
        back_button.click(
            show_login,
            outputs=[register_block, login_block, register_message]
        )
        
        # Registration form submission
        register_button.click(
            register_fn,
            inputs=[new_username, new_password, confirm_password],
            outputs=[register_block, login_block, login_message, new_username, 
                    new_password, confirm_password, register_message]
        )
        
        generate_button.click(
            generate_material,
            inputs=[disciplina_input, assunto_input, topicos_input, user_id],
            outputs=[markdown_output, pdf_output]
        ).then(
            load_study_plans,
            inputs=[user_id],
            outputs=[materials_table, gr.State([])]
        )
        
        # Function to refresh the study plan list
        refresh_button.click(
            load_study_plans,
            inputs=[user_id],
            outputs=[materials_table, gr.State([])]
        ).then(
            lambda visible_plans, full_plans: (gr.update(visible=False), gr.update(visible=True), "", full_plans),
            inputs=[materials_table, gr.State([])],
            outputs=[materials_table, gr.State([])]
        )

    return app

if __name__ == "__main__":
    app = main_app()
    app.launch()