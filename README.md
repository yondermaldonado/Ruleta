# Ruleta Casino (Pygame)

Ruleta europea (37 números, 0-36) con:

- Animación de la rueda girando con desaceleración realista (ease-out).
- Bolita que gira en sentido contrario y se frena hasta "caer" en el número.
- Sonidos generados **por código** (clics de la rueda, ficha, victoria, derrota)
  con `numpy` — no hay archivos de audio externos que empaquetar.
- Sistema de apuestas: Rojo, Negro, Par, Impar, Verde (0), con fichas de
  $10 / $50 / $100 / $500 y saldo virtual inicial de $1000.

## 1. Ejecutar en tu PC

```bash
pip install -r requirements.txt
python main.py
```

## 2. Convertirlo en un .exe (Windows)

Todo el juego es un único archivo (`main.py`) y no usa assets externos
(las imágenes se dibujan con `pygame.draw` y los sonidos se generan con
`numpy`), así que empaquetarlo es muy directo.

1. Instala PyInstaller (idealmente **desde Windows**, no desde Linux/Mac,
   porque PyInstaller genera un ejecutable para el sistema operativo en el
   que se ejecuta):

   ```bash
   pip install pyinstaller
   ```

2. Genera el ejecutable de un solo archivo, sin consola:

   ```bash
   pyinstaller --onefile --noconsole --name RuletaCasino main.py
   ```

3. El resultado queda en `dist/RuletaCasino.exe`. Ese es el archivo que
   puedes compartir; no necesita Python instalado en la máquina destino.

### Notas útiles

- Si PyInstaller se queja de módulos de `numpy` no encontrados, prueba:
  ```bash
  pyinstaller --onefile --noconsole --name RuletaCasino ^
      --hidden-import=numpy.core._methods ^
      --hidden-import=numpy.lib.format main.py
  ```
- Si quieres un ícono propio, agrega `--icon=mi_icono.ico` al comando.
- Es normal que algunos antivirus marquen como sospechoso un `.exe` hecho
  con `--onefile` (falso positivo muy común en PyInstaller); si molesta,
  usa `--onedir` en vez de `--onefile` (genera una carpeta en lugar de un
  único archivo, pero suele dar menos falsos positivos).
- Prueba siempre el `.exe` generado en una máquina Windows limpia antes de
  distribuirlo.

## 3. Personalizar

- `chip_values` — cambia los valores de las fichas disponibles.
- `SPIN_DURATION` — duración del giro en milisegundos.
- `make_tone(...)` — ajusta frecuencia/duración/tipo de onda para cambiar
  cualquier efecto de sonido.
- `BET_TYPES` — agrega nuevos tipos de apuesta y su multiplicador de pago.
