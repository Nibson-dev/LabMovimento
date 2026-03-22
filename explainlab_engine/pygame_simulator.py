#!/usr/bin/env python3
"""
pygame_simulator.py - Simulador 3D com Pygame para ExplainLab
"""

import pygame
import sys
from animations import VerticalMotionSimulator, MRUVSimulator, InclinedPlaneSimulator


class SimulatorApp:
    """Aplicacao principal de simulacao"""
    
    def __init__(self, width=1200, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("ExplainLab - Simulador 3D de Fisica")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60
        
        self.current_simulator = None
        self.state = "menu"
    
    def show_menu(self):
        """Mostra o menu principal"""
        font_title = pygame.font.Font(None, 48)
        font_option = pygame.font.Font(None, 36)
        
        menu_done = False
        selected = 0
        
        while menu_done is False and self.running:
            self.screen.fill((20, 20, 40))
            
            title = font_title.render("ExplainLab - Simulador 3D", True, (255, 200, 0))
            self.screen.blit(title, (self.width//2 - title.get_width()//2, 50))
            
            options = [
                "1. Lancamento Vertical / Queda Livre",
                "2. Movimento Retilineo Uniformemente Variado (MRUV)",
                "3. Plano Inclinado",
                "0. Sair"
            ]
            
            y_offset = 200
            for i, option in enumerate(options):
                color = (255, 255, 0) if i == selected else (200, 200, 200)
                text = font_option.render(option, True, color)
                self.screen.blit(text, (100, y_offset))
                y_offset += 80
            
            font_small = pygame.font.Font(None, 24)
            instr = font_small.render("Use SETAS para navegar, ENTER para selecionar, Q para sair", 
                                      True, (150, 150, 150))
            self.screen.blit(instr, (self.width//2 - instr.get_width()//2, self.height - 50))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    menu_done = True
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if selected == 0:
                            self.run_vertical_motion()
                            menu_done = True
                        elif selected == 1:
                            self.run_mruv()
                            menu_done = True
                        elif selected == 2:
                            self.run_inclined_plane()
                            menu_done = True
                        elif selected == 3:
                            self.running = False
                            menu_done = True
                    elif event.key == pygame.K_q:
                        self.running = False
                        menu_done = True
            
            self.clock.tick(self.fps)
    
    def run_vertical_motion(self):
        """Inicia a simulacao de lancamento vertical"""
        print("\n" + "="*50)
        print("  LANCAMENTO VERTICAL / QUEDA LIVRE")
        print("="*50)
        
        y0 = self._get_float_input("Altura inicial (y0) em metros [padrao: 0]: ", 0)
        v0 = self._get_float_input("Velocidade inicial (v0) em m/s [padrao: 15]: ", 15)
        g = self._get_float_input("Gravidade (g) em m/s2 [padrao: 9.8]: ", 9.8)
        
        print(f"\nOK! Iniciando simulacao: y0={y0}m, v0={v0}m/s, g={g}m/s2")
        print("Pressione SPACE para Play/Pause, R para Reset, Q para voltar\n")
        
        try:
            self.current_simulator = VerticalMotionSimulator(y0=y0, v0=v0, g=g)
            self._run_simulation()
        except Exception as e:
            print(f"ERRO na simulacao: {e}")
    
    def run_mruv(self):
        """Inicia a simulacao de MRUV"""
        print("\n" + "="*50)
        print("  MOVIMENTO RETILINEO UNIFORMEMENTE VARIADO")
        print("="*50)
        
        s0 = self._get_float_input("Posicao inicial (s0) em metros [padrao: 0]: ", 0)
        v0 = self._get_float_input("Velocidade inicial (v0) em m/s [padrao: 0]: ", 0)
        a = self._get_float_input("Aceleracao (a) em m/s2 [padrao: 2]: ", 2)
        t_final = self._get_float_input("Tempo final em segundos [padrao: 10]: ", 10)
        
        print(f"\nOK! Iniciando simulacao: s0={s0}m, v0={v0}m/s, a={a}m/s2, t={t_final}s")
        print("Pressione SPACE para Play/Pause, R para Reset, Q para voltar\n")
        
        try:
            self.current_simulator = MRUVSimulator(s0=s0, v0=v0, a=a, t_final=t_final)
            self._run_simulation()
        except Exception as e:
            print(f"ERRO na simulacao: {e}")
    
    def run_inclined_plane(self):
        """Inicia a simulacao de plano inclinado"""
        print("\n" + "="*50)
        print("  PLANO INCLINADO")
        print("="*50)
        
        m = self._get_float_input("Massa (m) em kg [padrao: 5]: ", 5)
        theta = self._get_float_input("Angulo (theta) em graus [padrao: 30]: ", 30)
        g = self._get_float_input("Gravidade (g) em m/s2 [padrao: 9.8]: ", 9.8)
        mu = self._get_float_input("Coeficiente de atrito (mu) [padrao: 0]: ", 0)
        
        print(f"\nOK! Iniciando simulacao: m={m}kg, theta={theta}graus, g={g}m/s2, mu={mu}")
        print("Pressione SPACE para Play/Pause, R para Reset, Q para voltar\n")
        
        try:
            self.current_simulator = InclinedPlaneSimulator(m=m, theta=theta, g=g, mu=mu)
            self._run_simulation()
        except Exception as e:
            print(f"ERRO na simulacao: {e}")
    
    def _run_simulation(self):
        """Loop principal da simulacao"""
        if self.current_simulator is None:
            return
        
        simulation_running = True
        
        while simulation_running and self.running:
            dt = self.clock.tick(self.fps) / 1000.0
            
            self.current_simulator.update(dt)
            self.current_simulator.draw(self.screen, self.width, self.height)
            self._draw_explanation(self.current_simulator.get_explanation_steps())
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    simulation_running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.current_simulator.toggle_play()
                    elif event.key == pygame.K_r:
                        self.current_simulator.reset()
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.current_simulator.increase_speed()
                    elif event.key == pygame.K_MINUS:
                        self.current_simulator.decrease_speed()
                    elif event.key == pygame.K_q:
                        simulation_running = False
    
    def _draw_explanation(self, steps):
        """Desenha os passos da explicacao no canto direito"""
        if not steps:
            return
        
        panel_x = self.width - 350
        panel_width = 340
        panel_height = self.height
        
        pygame.draw.rect(self.screen, (30, 30, 50), (panel_x, 0, panel_width, panel_height))
        pygame.draw.line(self.screen, (100, 100, 150), (panel_x, 0), (panel_x, panel_height), 2)
        
        font_title = pygame.font.Font(None, 20)
        title = font_title.render("Passos da Solucao", True, (255, 200, 0))
        self.screen.blit(title, (panel_x + 10, 10))
        
        font_small = pygame.font.Font(None, 14)
        y_offset = 40
        
        for i, step in enumerate(steps[:8]):
            if y_offset > self.height - 50:
                break
            
            step_text = f"{step['step']}. {step['title']}"
            text = font_small.render(step_text, True, (200, 200, 255))
            self.screen.blit(text, (panel_x + 10, y_offset))
            y_offset += 25
            
            eq_text = step['equation_latex'][:40] + "..." if len(step['equation_latex']) > 40 else step['equation_latex']
            eq = font_small.render(eq_text, True, (150, 255, 150))
            self.screen.blit(eq, (panel_x + 15, y_offset))
            y_offset += 20
        
        if len(steps) > 8:
            font_tiny = pygame.font.Font(None, 12)
            more_text = font_tiny.render("... (mais passos)", True, (150, 150, 150))
            self.screen.blit(more_text, (panel_x + 10, y_offset))
    
    def _get_float_input(self, prompt, default):
        """Coleta input do usuario no terminal"""
        try:
            user_input = input(prompt).strip()
            if user_input == "":
                return default
            return float(user_input)
        except ValueError:
            print(f"AVISO: Entrada invalida, usando padrao: {default}")
            return default
    
    def run(self):
        """Loop principal da aplicacao"""
        print("\n" + "="*60)
        print("  BEM-VINDO AO EXPLAINLAB - SIMULADOR 3D DE FISICA")
        print("="*60)
        print("\nUse as SETAS do teclado para navegar no menu")
        print("Pressione ENTER para selecionar uma opcao")
        print("Pressione Q para sair\n")
        
        while self.running:
            self.show_menu()
        
        pygame.quit()
        print("\nAte logo!\n")
        sys.exit()


def main():
    """Funcao principal"""
    app = SimulatorApp(width=1600, height=900)
    app.run()


if __name__ == "__main__":
    main()