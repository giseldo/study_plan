from supabase import create_client
import util

SUPABASE_URL = "https://wlriuezvfrsqfkvalabq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indscml1ZXp2ZnJzcWZrdmFsYWJxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA4ODA1OTAsImV4cCI6MjA1NjQ1NjU5MH0.syhO_hTeiJb3To4_jAn2h9kXl0uDw_noMXTOuQwnwgE"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Login function using Supabase
def login(username, password):
    try:
        # Query the 'usuario' table in Supabase
        response = supabase.table('usuario').select('*').eq('login', username).execute()
        
        # Check if user exists and password matches
        if response.data and len(response.data) > 0:
            stored_hash = response.data[0].get('senha')
            if stored_hash == util.hash_password(password):
                return True, f"Bem-vindo, {username}!", response.data[0].get('id')
            else:
                return False, "Senha incorreta. Tente novamente.", None
        else:
            return False, "Usuário não encontrado. Tente novamente.", None
            
    except Exception as e:
        print(f"Error during login: {e}")
        return False, "Erro ao fazer login. Por favor, tente novamente.", None
    
# Function to save study plan to database
def save_study_plan(markdown_content, user_id):
    try:
        # Insert the study plan into the plano_estudo table
        response = supabase.table('plano_estudo').insert({
            "texto_plano": markdown_content,
            "id_usuario": user_id
        }).execute()
        
        # Check if insertion was successful
        if response.data:
            plan_id = response.data[0].get('id')
            return True, plan_id
        else:
            return False, None
            
    except Exception as e:
        print(f"Error saving study plan: {e}")
        return False, None
    
# New registration function using Supabase
def register_user(username, password, confirm_password):
    try:
        # Check if passwords match
        if password != confirm_password:
            return False, "As senhas não coincidem. Tente novamente."
        
        # Check if username already exists
        response = supabase.table('usuario').select('*').eq('login', username).execute()
        if response.data and len(response.data) > 0:
            return False, "Nome de usuário já existe. Escolha outro."
        
        # Hash the password
        hashed_password = util.hash_password(password)
        
        # Insert new user
        response = supabase.table('usuario').insert({
            "login": username, 
            "senha": hashed_password
        }).execute()
        
        # Check if insertion was successful
        if response.data:
            return True, "Cadastro realizado com sucesso! Você pode fazer login agora."
        else:
            return False, "Erro ao cadastrar usuário. Tente novamente."
            
    except Exception as e:
        print(f"Error during registration: {e}")
        return False, "Erro ao realizar cadastro. Por favor, tente novamente."
    
# Function to retrieve study plans from database
def get_user_study_plans(user_id):
    try:
        # Query the 'plano_estudo' table for all study plans of the user
        response = supabase.table('plano_estudo').select('*').eq('id_usuario', user_id).execute()
        
        if response.data:
            # Return the data in a format suitable for gradio table
            table_data = []
            for plan in response.data:
                # Extract relevant information from the plan
                plan_id = plan.get('id')
                # Extract title from the content or use a default title
                content = plan.get('texto_plano', '')
                title = "Material de Estudo"
                
                # Try to extract a title from the markdown content
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                
                created_at = plan.get('created_at', '').split('T')[0]  # Format date
                
                table_data.append([plan_id, title, created_at, content])
            
            return table_data
        else:
            return []
            
    except Exception as e:
        print(f"Error retrieving study plans: {e}")
        return []