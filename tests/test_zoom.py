import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_zoom_credentials():
    print("🔍 Verificando credenciales de Zoom...")
    
    required = ['ZOOM_API_KEY', 'ZOOM_API_SECRET', 'ZOOM_ACCOUNT_ID']
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        print(f"❌ Variables faltantes: {', '.join(missing)}")
        return False
    
    print("✅ Credenciales configuradas")
    return True

def test_zoom_meeting():
    print("📹 Probando creación de reunión en Zoom...")
    
    try:
        from bot_ortopedia import create_zoom_meeting
        
        meeting = create_zoom_meeting("Prueba de Consulta", 30)
        
        if meeting:
            print(f"✅ Reunión creada: {meeting['join_url']}")
            return True
        else:
            print("❌ No se pudo crear la reunión")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if test_zoom_credentials() and test_zoom_meeting():
        print("\n✅ TODAS LAS PRUEBAS DE ZOOM PASARON")
        sys.exit(0)
    else:
        print("\n❌ PRUEBAS FALLIDAS")
        sys.exit(1)
