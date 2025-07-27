import pygame
import sys
import subprocess  # For running external file dialog as a separate process

def open_file_dialog_subprocess():
    # Calls an external script to open a file dialog and returns the selected path.
    result = subprocess.run(
        ["python3", "audio_file_dialog_wx.py"],  # Launch wxPython-based file picker
        capture_output=True,                     # Capture output printed to stdout
        text=True                                # Return captured output as a string
    )
    file_path = result.stdout.strip()            # Get the file path, if any
    return file_path or None                     # Return the chosen path, or None if canceled

def show_instruction_screen():
    pygame.init()                                  
    font_inst = pygame.font.Font("./resources/fonts/Wash Your Hand.ttf", 30)        
    font_button = pygame.font.Font("./resources/fonts/Super Comic.ttf", 20)
    screen = pygame.display.set_mode((620, 550))  
    background = pygame.image.load("./resources/images/background_welcome_screen.png")
    click_sound = pygame.mixer.Sound("./resources/sounds/click.wav")
    clock = pygame.time.Clock()
    instructions = [
        "Welcome to the Frog Jam!",
        "Click the button below to upload an audio file.",
        "Visualization will start after file selection."
    ]
    button_rect = pygame.Rect(340, 450, 250, 60)      # Define button size and position
    button_text = font_button.render("Upload Audio File", True, (0,0,0))  # Render button text



    # Colors
    main_color = (255, 215, 0)      # Gold/yellow
    hover_color = (255, 165, 0)     # Lighter yellow when hovered
    border_color = (20, 20, 20)     # Black border
    shadow_color = (70, 70, 50)     # Dark shadow


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:       # Window closed
                pygame.quit()
                sys.exit(0)
            # If user clicks inside the button
            elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                # Play in the button click event:
                click_sound.play()
                audio_path = open_file_dialog_subprocess()   # Open file dialog as subprocess
                if audio_path:                  # If a file was selected
                    pygame.quit()               # Close instruction (welcome) window
                    return audio_path           # Pass file path back to main program

        y = 30
        screen.blit(background, (0, 0))
        for line in instructions:
            txt_surf = font_inst.render(line, True, (255,255,255))
            # Center each line horizontally
            screen.blit(txt_surf, (screen.get_width()//2 - txt_surf.get_width()//2, y))
            y += 50
        
        # Determine if mouse is over the button
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_pos)
        
        # Decide current color
        current_color = hover_color if is_hovered else main_color


        # Draw drop shadow (slightly down and to the right)
        shadow_rect = button_rect.move(8, 8)
        pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=16)

        # Draw border (using a slightly larger rect)
        border_rect = button_rect.inflate(10, 10)
        pygame.draw.rect(screen, border_color, border_rect, border_radius=16)

        # Draw main button rectangle
        pygame.draw.rect(screen, current_color, button_rect, border_radius=12)

        # Draw centered, bold button text
        #button_text = font_inst.render("Upload Audio File", True, (0,0,0))
        text_x = button_rect.x + (button_rect.width - button_text.get_width()) // 2
        text_y = button_rect.y + (button_rect.height - button_text.get_height()) // 2
        screen.blit(button_text, (text_x, text_y))

        
        #pygame.draw.rect(screen, button_color, button_rect, border_radius=8)  # Draw the upload button
        #screen.blit(button_text, (button_rect.x + 20, button_rect.y + 15))  # Draw the text on the button
        pygame.display.flip()                  # Update the display
        clock.tick(60)                         # Limit frame rate to 60 FPS
