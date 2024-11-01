import os
import random
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
from keep_alive import run
import time

# Cargar las variables de entorno
load_dotenv()

# Crear los intents
intents = nextcord.Intents.default()
intents.messages = True
intents.message_content = True  # Habilita el intent de contenido de mensajes
intents.guilds = True  # Necesario para acceder a los roles

# Configurar el bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Inicializar las listas y variables
números = list(range(1, 76))
números_salidos = []
juegos_jugados = 0
compras_realizadas = {}  # Almacena las compras de cada usuario

# Cambiar la presencia del bot al iniciar
@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Game(name="Bingo Online"))
    print(f'Bot conectado como {bot.user}')

# Función para generar un número de Bingo
def sacar_numero():
    if not números:
        return None
    número = random.choice(números)
    números.remove(número)
    return número

# Función para obtener la letra correspondiente a un número
def obtener_letra(número):
    if 1 <= número <= 15:
        return 'B'
    elif 16 <= número <= 30:
        return 'I'
    elif 31 <= número <= 45:
        return 'N'
    elif 46 <= número <= 60:
        return 'G'
    elif 61 <= número <= 75:
        return 'O'
    return None  # En caso de un número inválido

# Comando Slash para jugar al Bingo
@bot.slash_command(name="bingo", description="Saca un número de Bingo.")
async def bingo(interaction: nextcord.Interaction):
    global juegos_jugados, números_salidos
    juegos_jugados += 1
    número = sacar_numero()
    
    if número is not None:
        letra = obtener_letra(número)
        números_salidos.append((letra, número))
        
        embed = nextcord.Embed(title="Número de Bingo", description=f"¡El número es {letra}{número}!", color=0x00ff00)
        salida_formateada = ', '.join([f"{letra}{num}" for letra, num in números_salidos])
        embed.add_field(name="Números salidos", value=salida_formateada, inline=False)
        
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("¡Todos los números han salido! Usa `/reiniciar` para jugar de nuevo.")

# Comando Slash para reiniciar el juego
@bot.slash_command(name="reiniciar", description="Reinicia el juego y restablece los números.")
async def reiniciar(interaction: nextcord.Interaction):
    global números, números_salidos
    números = list(range(1, 76))
    números_salidos.clear()
    await interaction.response.send_message("¡El juego ha sido reiniciado! Usa `/bingo` para sacar un número.")

# Comando Slash de ayuda
@bot.slash_command(name="ayuda", description="Muestra los comandos de Bingo.")
async def ayuda(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="Comandos de Bingo", color=0x007bff)
    embed.add_field(name="/bingo", value="Saca un número de Bingo.", inline=False)
    embed.add_field(name="/reiniciar", value="Reinicia el juego y restablece los números.", inline=False)
    embed.add_field(name="/ayuda", value="Muestra esta ayuda.", inline=False)
    embed.add_field(name="/comprar_cartones", value="Compra múltiples cartones de Bingo.", inline=False)
    embed.add_field(name="/compras", value="Muestra la lista de compras realizadas.", inline=False)
    embed.set_footer(text="¡Diviértete jugando al Bingo!")
    await interaction.response.send_message(embed=embed)

# Comando Slash para ver estadísticas
@bot.slash_command(name="estadisticas", description="Muestra las estadísticas del juego.")
async def estadisticas(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="Estadísticas del Juego", color=0xffcc00)
    embed.add_field(name="Números jugados ", value=juegos_jugados, inline=False)
    embed.add_field(name="Números restantes", value=len(números), inline=False)
    await interaction.response.send_message(embed=embed)

# Comando Slash para comprar cartones
@bot.slash_command(name="comprar_cartones", description="Compra múltiples cartones de Bingo.")
async def comprar_cartones(interaction: nextcord.Interaction, cantidad: int, cartones: str):
    canal_id = 1300321788416491570  # ID del canal donde se enviará el mensaje
    canal = bot.get_channel(canal_id)

    # Validar que el canal existe
    if canal is None:
        await interaction.response.send_message("El canal no se encuentra disponible.", ephemeral=True)
        return

    # Validar la cantidad
    if cantidad <= 0 or cantidad > 100:
        await interaction.response.send_message("Por favor, proporciona una cantidad válida de cartones (1-50).", ephemeral=True)
        return

    # Actualizar las compras del usuario
    user_id = interaction.user.id
    current_time = time.time()

    # Comprobar si el usuario ya ha comprado estos cartones en las últimas 2 horas
    if user_id in compras_realizadas:
        last_purchase_time, _ = compras_realizadas[user_id]
        if current_time - last_purchase_time < 7200:  # 2 horas
            await interaction.response.send_message("No puedes comprar cartones nuevamente en menos de 2 horas.", ephemeral=True)
            return

    # Guardar la compra con la marca de tiempo
    compras_realizadas[user_id] = (current_time, cartones)

    # Mensaje de compra
    embed = nextcord.Embed(title="Compra de Cartones", color=0x1abc9c)
    embed.add_field(name="Comprador", value=f"{interaction.user.mention} (ID: {interaction.user.id})", inline=False)
    embed.add_field(name="Cantidad de Cartones Comprados", value=cantidad, inline=False)
    embed.add_field(name="Números de los Cartones", value=cartones, inline=False)
    embed.set_footer(text="¡Buena suerte en el Bingo!")

    # Intentar enviar el mensaje al canal
    try:
        await canal.send(embed=embed)
        await interaction.response.send_message(f"¡Has comprado {cantidad} cartones! Se ha notificado en el canal.", ephemeral=True)
    except Exception as e:
        print(f"Error al enviar el mensaje: {e}")
        await interaction.response.send_message("Hubo un error al notificar la compra en el canal.", ephemeral=True)

# Comando Slash para ver la lista de compras
@bot.slash_command(name="compras", description="Muestra la lista de compras realizadas.")
async def compras(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="Lista de Compras de Cartones", color=0x3498db)
    
    if not compras_realizadas:
        embed.add_field(name="Sin Compras", value="No hay compras registradas.", inline=False)
    else:
        for user_id, (timestamp, cartones) in compras_realizadas.items():
            user = await bot.fetch_user(user_id)
            tiempo_compra = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
            embed.add_field(name=f"Comprador: {user.mention}", value=f"Números: {cartones}\nFecha de Compra: {tiempo_compra}", inline=False)

    await interaction.response.send_message(embed=embed)

# Iniciar el servidor Flask en un hilo separado
import threading
threading.Thread(target=run).start()

# Iniciar el bot usando el token de las variables de entorno
bot.run(os.getenv('DISCORD_TOKEN'))