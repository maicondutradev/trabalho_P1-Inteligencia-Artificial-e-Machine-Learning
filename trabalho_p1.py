import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import List, Dict
import random
import threading
import time

@dataclass
class Contexto:
    area: str
    nivel: str
    prioridade: str
    prazo: str
    multiplataforma: bool
    trabalho_equipe: bool

@dataclass
class Resultado:
    linguagem_principal: str
    linguagem_secundaria: str
    confianca: float
    info_texto: str
    razoes: List[str]
    alertas: List[str]
    frameworks: List[str]

class MotorDecisao:
    BASE_SCORES = {
        "ia_data": {"Python": 90.0, "C++": 45.0, "Java": 30.0, "TypeScript": 20.0, "Go": 20.0, "Rust": 25.0, "C#": 15.0, "Kotlin/Swift": 10.0},
        "web": {"TypeScript": 80.0, "Java": 75.0, "C#": 70.0, "Python": 65.0, "Go": 65.0, "Rust": 45.0, "Kotlin/Swift": 10.0, "C++": 15.0},
        "mobile": {"Kotlin/Swift": 90.0, "TypeScript": 70.0, "C#": 45.0, "Java": 35.0, "C++": 25.0, "Python": 15.0, "Go": 15.0, "Rust": 15.0},
        "sistemas": {"Rust": 85.0, "C++": 85.0, "Go": 70.0, "C#": 35.0, "Python": 25.0, "Java": 25.0, "TypeScript": 15.0, "Kotlin/Swift": 10.0},
        "jogos": {"C#": 85.0, "C++": 85.0, "Python": 35.0, "Rust": 35.0, "TypeScript": 25.0, "Java": 20.0, "Kotlin/Swift": 20.0, "Go": 15.0},
        "automacao": {"Python": 90.0, "Go": 65.0, "TypeScript": 55.0, "Rust": 35.0, "C#": 30.0, "Java": 25.0, "C++": 20.0, "Kotlin/Swift": 10.0}
    }

    MODS = {
        "prioridade": {
            "performance": {"Rust": 35, "C++": 35, "Go": 20, "Kotlin/Swift": 25, "C#": 10, "Java": 10, "TypeScript": -10, "Python": -15},
            "velocidade_dev": {"Python": 25, "TypeScript": 25, "Go": 15, "C#": 10, "Rust": -15, "C++": -20},
            "aprendizado": {"Python": 30, "TypeScript": 20, "Go": 15, "C#": 10, "Rust": -25, "C++": -30},
            "mercado": {"Java": 25, "TypeScript": 20, "Python": 20, "C#": 20, "Go": 15, "Kotlin/Swift": 15}
        },
        "nivel": {
            "iniciante": {"Python": 20, "TypeScript": 15, "Go": 10, "Rust": -25, "C++": -30},
            "intermediario": {"Java": 15, "TypeScript": 10, "Go": 10, "C#": 10},
            "avancado": {"Rust": 25, "C++": 25, "Go": 15}
        },
        "prazo": {
            "curto": {"Python": 15, "TypeScript": 15, "Go": 10, "C++": -15, "Rust": -15},
            "longo": {"Java": 25, "C#": 20, "Rust": 15, "C++": 15}
        }
    }

    STACK_INFO = {
        ("Python", "ia_data"): ("🐍 Python - O ecossistema padrão da indústria para Inteligência Artificial, Machine Learning e Ciência de Dados.", ["PyTorch / TensorFlow", "Hugging Face / LangChain", "Pandas & Scikit-Learn"]),
        ("Python", "web"): ("🐍 Python - Backend ágil e produtivo, ideal para APIs RESTful, microsserviços e processamento assíncrono.", ["FastAPI", "Django", "SQLAlchemy / Pydantic"]),
        ("Python", "automacao"): ("🐍 Python - Referência absoluta em automação de tarefas, web scraping, scripts e manipulação de dados.", ["Playwright / Selenium", "BeautifulSoup / Scrapy", "Typer / Click"]),
        ("Python", "jogos"): ("🐍 Python - Excelente para prototipagem rápida de jogos, lógica de scripts e motores como Godot e Pygame.", ["Godot Engine (GDScript/Python)", "Pygame Community", "Ursina Engine"]),
        ("TypeScript", "web"): ("🟦 TypeScript / JS - O padrão definitivo para desenvolvimento Web Fullstack moderno, Frontend e ecossistema Node/React.", ["React / Next.js", "Node.js / NestJS", "TailwindCSS"]),
        ("TypeScript", "mobile"): ("📱 TypeScript (React Native / Expo) - Desenvolvimento mobile multiplataforma ágil compartilhando a mesma base de código.", ["React Native", "Expo Framework", "NativeWind / Tamagui"]),
        ("TypeScript", "automacao"): ("🟦 TypeScript - Eficiente para scripts com tipagem estática, automação via Node.js e ferramentas CLI.", ["Playwright (TS)", "Commander.js", "Prisma / Zod"]),
        ("Rust", "sistemas"): ("🦀 Rust - Máxima performance e concorrência sem coletor de lixo, com garantia estrita de segurança de memória.", ["Tokio", "Tauri", "Rayon / Crossbeam"]),
        ("Rust", "web"): ("🦀 Rust - Backend de altíssima vazão, microsserviços ultra-rápidos e consumo mínimo de recursos de CPU/RAM.", ["Axum", "Actix-web", "Tower / SQLx"]),
        ("Rust", "jogos"): ("🦀 Rust - Ideal para novos motores gráficos e desenvolvimento de jogos com foco em segurança e concorrência.", ["Bevy Engine", "Macroquad", "wgpu"]),
        ("Go", "sistemas"): ("🔵 Go (Golang) - Linguagem moderna para infraestrutura em nuvem, ferramentas de sistema e serviços concorrentes.", ["Cobra CLI", "Viper", "Docker & K8s SDKs"]),
        ("Go", "web"): ("🔵 Go (Golang) - Alta performance backend, rápida compilação e simplicidade em arquiteturas de microsserviços.", ["Gin / Fiber", "Echo", "GORM / sqlx"]),
        ("Go", "automacao"): ("🔵 Go (Golang) - Criação de utilitários CLI compilados em binário único, leves e de fácil distribuição.", ["Colly (Scraping)", "Go-Rod", "Bubbletea (TUI)"]),
        ("C#", "jogos"): ("🟣 C# - A linguagem dominante no desenvolvimento de jogos através da Unity Engine e suporte amplo no Godot.", ["Unity Engine", "Godot Engine (C#)", "MonoGame / Raylib-cs"]),
        ("C#", "web"): ("🟣 C# (.NET Core) - Ecossistema corporativo completo, de alta performance e escalabilidade para APIs e backends.", ["ASP.NET Core Web API", "Entity Framework Core", "Blazor"]),
        ("C#", "sistemas"): ("🟣 C# - Desenvolvimento de aplicações desktop e serviços Windows/.NET com ampla biblioteca padrão.", [".NET Desktop / WPF", "MAUI", "Avalonia UI"]),
        ("C++", "jogos"): ("⚡ C++ - Padrão da indústria para jogos AAA de altíssimo desempenho, motores gráficos e Unreal Engine.", ["Unreal Engine", "DirectX 12 / Vulkan", "Raylib / SDL2"]),
        ("C++", "sistemas"): ("⚡ C++ - Controle total sobre hardware, sistemas embarcados, drivers e máxima eficiência computacional.", ["Boost Libraries", "Qt Framework", "CMake / Conan"]),
        ("C++", "ia_data"): ("⚡ C++ - Essencial para otimização de baixo nível em tensores, aceleração CUDA e inferência de alta performance.", ["CUDA Toolkit", "LibTorch (PyTorch C++)", "ONNX Runtime C++"]),
        ("Kotlin/Swift", "mobile"): ("📱 Kotlin / Swift - Desenvolvimento mobile nativo oficial focado em ecossistemas Android (Kotlin) e iOS (Swift).", ["Jetpack Compose (Android)", "SwiftUI (iOS)", "Kotlin Multiplatform (KMP)"]),
        ("Java", "web"): ("☕ Java - Sólido e consolidado para sistemas corporativos de grande porte, microsserviços e alta resiliência.", ["Spring Boot 3", "Quarkus", "Micronaut / Hibernate"]),
        ("Java", "ia_data"): ("☕ Java - Utilizado em engenharia de dados em larga escala, ecossistema Apache (Hadoop/Spark) e pipelines.", ["Apache Spark", "Apache Kafka", "Deeplearning4j"])
    }

    DEFAULT_INFO = {
        "Python": ("🐍 Python - Excelente legibilidade, rápida prototipagem e vasto ecossistema.", ["Bibliotecas padrão", "NumPy", "Requests"]),
        "TypeScript": ("🟦 TypeScript / JS - Sintaxe moderna com tipagem estática e suporte multiplataforma.", ["Node.js", "TypeScript Compiler", "NPM Ecosystem"]),
        "Rust": ("🦀 Rust - Performance extrema, segurança de memória e alta confiabilidade.", ["Cargo", "Tokio", "Serde"]),
        "Go": ("🔵 Go (Golang) - Simplicidade, concorrência nativa eficiente e compilação rápida.", ["Go Standard Library", "Go Modules"]),
        "C#": ("🟣 C# - Linguagem madura, fortemente tipada e com amplo suporte corporativo.", [".NET Base Class Library", "NuGet Packages"]),
        "C++": ("⚡ C++ - Controle total sobre recursos de máquina e padrão para sistemas críticos.", ["Standard Template Library (STL)", "Boost"]),
        "Kotlin/Swift": ("📱 Kotlin / Swift - Linguagens modernas, expressivas e padrão oficial para mobile.", ["Android Jetpack / Apple SDKs"]),
        "Java": ("☕ Java - Estabilidade comprovada, portabilidade e liderança corporativa.", ["Java Virtual Machine (JVM)", "Maven / Gradle"])
    }

    def analisar(self, ctx: Contexto) -> Resultado:
        scores: Dict[str, float] = dict(self.BASE_SCORES.get(ctx.area, {}))

        for categoria, valor in [("prioridade", ctx.prioridade), ("nivel", ctx.nivel), ("prazo", ctx.prazo)]:
            for lang, delta in self.MODS[categoria].get(valor, {}).items():
                scores[lang] = scores.get(lang, 0.0) + delta

        if ctx.multiplataforma:
            for lang in ["TypeScript", "Python", "Go", "Java", "C#"]:
                scores[lang] = scores.get(lang, 0.0) + 10.0
            if ctx.area == "mobile":
                scores["TypeScript"] += 15.0
                scores["Kotlin/Swift"] -= 5.0
        elif ctx.area == "mobile":
            scores["Kotlin/Swift"] += 25.0

        if ctx.trabalho_equipe:
            for lang in ["TypeScript", "Java", "C#", "Go", "Rust"]:
                scores[lang] = scores.get(lang, 0.0) + (10.0 if lang == "Rust" else 15.0)

        ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top1, score_top1 = ranking[0]
        top2, score_top2 = ranking[1]

        diferenca = score_top1 - score_top2
        confianca = min(98.5, max(62.0, 72.0 + (diferenca * 0.7) + random.uniform(-1.5, 1.5)))

        info_texto, frameworks = self.STACK_INFO.get((top1, ctx.area), self.DEFAULT_INFO.get(top1, ("", [])))
        razoes = self._gerar_razoes(top1, ctx)
        alertas = self._gerar_alertas(top1, ctx, diferenca)

        return Resultado(
            linguagem_principal=top1,
            linguagem_secundaria=top2,
            confianca=confianca,
            info_texto=info_texto,
            razoes=razoes,
            alertas=alertas,
            frameworks=frameworks
        )

    def _gerar_razoes(self, top: str, ctx: Contexto) -> List[str]:
        razoes = []
        desc_area = {
            ("Python", "ia_data"): "Python possui o ecossistema mais avançado e consolidado para Inteligência Artificial, Machine Learning e manipulação de tensores.",
            ("Python", "web"): "Python com frameworks modernos (FastAPI/Django) permite criar APIs limpas, robustas e altamente produtivas.",
            ("Python", "automacao"): "Python é a ferramenta líder em automação, scraping e scripts por sua simplicidade de escrita e vasto acervo de bibliotecas.",
            ("Python", "jogos"): "Excelente para prototipagem rápida e desenvolvimento ágil de jogos 2D/indie.",
            ("TypeScript", "web"): "TypeScript é a tecnologia padrão para a Web moderna, permitindo unificar a linguagem entre o Frontend e o Backend.",
            ("TypeScript", "mobile"): "TypeScript com React Native/Expo permite desenvolver para Android e iOS a partir de uma única base de código com excelente velocidade.",
            ("TypeScript", "automacao"): "Permite construir utilitários e automações com tipagem estática e ecossistema moderno via Node.js.",
            ("Kotlin/Swift", "mobile"): "Linguagens nativas (Kotlin para Android e Swift para iOS) entregam desempenho máximo, fluidez de UI e acesso total ao hardware.",
            ("Rust", "sistemas"): "Rust oferece controle de baixo nível de memória com garantias matemáticas de segurança e concorrência sem sobrecarga de garbage collector.",
            ("Rust", "web"): "Oferece microserviços e APIs de latência ultrabaixa com consumo mínimo de recursos de servidor.",
            ("Rust", "jogos"): "Ideal para arquitetura ECS e motores de jogos com máxima eficiência de threads.",
            ("Go", "sistemas"): "Go oferece excelente modelo de concorrência com goroutines, compilação ultrarrápida para binário único e simplicidade de manutenção.",
            ("Go", "web"): "Go oferece excelente modelo de concorrência com goroutines, compilação ultrarrápida para binário único e simplicidade de manutenção.",
            ("Go", "automacao"): "Go oferece excelente modelo de concorrência com goroutines, compilação ultrarrápida para binário único e simplicidade de manutenção.",
            ("C#", "jogos"): "C# é a principal linguagem da Unity Engine, oferecendo o melhor equilíbrio entre produtividade, suporte a física e ecossistema de assets.",
            ("C#", "web"): "ASP.NET Core é um dos frameworks web mais rápidos do mercado, ideal para serviços empresariais escaláveis.",
            ("C++", "jogos"): "C++ oferece máxima taxa de quadros e controle minucioso de hardware, sendo a escolha mandatória para motores AAA como a Unreal Engine.",
            ("C++", "sistemas"): "C++ oferece máxima taxa de quadros e controle minucioso de hardware, permitindo extrair desempenho extremo.",
            ("C++", "ia_data"): "Essencial para operações pesadas de tensores, kernels CUDA e execução em tempo real.",
            ("Java", "web"): "Java é o padrão corporativo por sua alta estabilidade, suporte a microsserviços pesados e maturidade de bibliotecas empresariais."
        }
        if (top, ctx.area) in desc_area:
            razoes.append(desc_area[(top, ctx.area)])

        if ctx.prioridade == "performance" and top in ("Rust", "C++", "Go", "Kotlin/Swift", "C#"):
            razoes.append(f"O requisito de Performance Extrema é plenamente atendido pela compilação nativa/otimizada de {top}.")
        elif ctx.prioridade == "velocidade_dev" and top in ("Python", "TypeScript", "Go", "C#"):
            razoes.append(f"A prioridade em Velocidade de Desenvolvimento é favorecida pela alta produtividade e sintaxe expressiva de {top}.")
        elif ctx.prioridade == "aprendizado" and top in ("Python", "TypeScript", "Go"):
            razoes.append(f"A curva de aprendizado acessível de {top} viabiliza rápida evolução técnica sem sobrecarga desnecessária.")
        elif ctx.prioridade == "mercado" and top in ("TypeScript", "Python", "Java", "C#", "Go", "Kotlin/Swift"):
            razoes.append(f"Forte demanda e alto volume de oportunidades no mercado profissional para especialistas em {top}.")

        if ctx.nivel == "iniciante" and top in ("Python", "TypeScript", "Go"):
            razoes.append(f"A vasta comunidade e material didático disponível para {top} facilitam o acolhimento para o nível iniciante.")
        elif ctx.nivel == "avancado" and top in ("Rust", "C++", "Go", "C#", "Java"):
            razoes.append(f"Seu domínio técnico avançado permite explorar todo o potencial de arquitetura, concorrência e tipagem de {top}.")

        if ctx.multiplataforma and top in ("TypeScript", "Python", "Java", "C#", "Go"):
            razoes.append("Arquitetura e suporte nativo para múltiplos sistemas operacionais sem necessidade de reescrita total.")

        if ctx.trabalho_equipe and top in ("TypeScript", "Java", "C#", "Go", "Rust"):
            razoes.append("Tipagem estática e ecossistema maduro que facilitam a colaboração e manutenibilidade em times maiores.")

        return razoes

    def _gerar_alertas(self, top: str, ctx: Contexto, diferenca: float) -> List[str]:
        alertas = []
        if ctx.nivel == "iniciante" and top in ("Rust", "C++"):
            alertas.append("Curva íngreme: Gerenciamento manual de memória e ciclo de vida de ponteiros exigem estudo aprofundado para iniciantes.")
        if ctx.prazo == "curto" and top in ("Rust", "C++", "Java"):
            alertas.append("Prazo reduzido: Evite complexidade arquitetural excessiva; aproveite bibliotecas prontas para viabilizar a entrega.")
        if ctx.area == "mobile" and ctx.multiplataforma and top == "Kotlin/Swift":
            alertas.append("Atenção Multiplataforma: Para cobrir Android e iOS com código nativo, considere Kotlin Multiplatform (KMP) ou time capacitado em ambas as plataformas.")
        if ctx.area == "mobile" and top == "TypeScript" and ctx.prioridade == "performance":
            alertas.append("Trade-off de Performance: Para processamento gráfico 3D ou cálculos pesados em tempo real, crie módulos nativos complementares em Kotlin/Swift ou C++.")
        if diferenca < 6.0:
            alertas.append("Margem competitiva: A segunda opção também é altamente viável e pode ser escolhida caso o time já possua experiência prévia nela.")
        return alertas

class AppRecomendadorLinguagem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Recomendador de Linguagem de Programação")
        self.geometry("1100x720")
        self.minsize(1000, 680)

        self.COLOR_BG = "#1e1e2e"
        self.COLOR_CARD = "#2a2a3c"
        self.COLOR_CARD_BORDER = "#3b3b54"
        self.COLOR_TEXT = "#cdd6f4"
        self.COLOR_TEXT_MUTED = "#9399b2"
        self.COLOR_ACCENT = "#00f5d4"
        self.COLOR_PURPLE = "#b4befe"
        self.COLOR_SUCCESS = "#a6e3a1"
        self.COLOR_WARNING = "#f9e2af"

        self.configure(bg=self.COLOR_BG)
        self.motor = MotorDecisao()
        self._stream_id = 0

        self._configurar_estilos()
        self._construir_interface()

    def _configurar_estilos(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure(".", background=self.COLOR_BG, foreground=self.COLOR_TEXT)
        self.style.configure("Card.TFrame", background=self.COLOR_CARD, relief="flat")
        self.style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground=self.COLOR_ACCENT, background=self.COLOR_BG)
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 10), foreground=self.COLOR_TEXT_MUTED, background=self.COLOR_BG)
        self.style.configure("CardTitle.TLabel", font=("Segoe UI", 12, "bold"), foreground=self.COLOR_PURPLE, background=self.COLOR_CARD)
        self.style.configure("FieldLabel.TLabel", font=("Segoe UI", 10, "bold"), foreground=self.COLOR_TEXT, background=self.COLOR_CARD)
        self.style.configure("TCombobox", fieldbackground="#313244", background="#45475a", foreground="#ffffff", borderwidth=0)
        self.style.map("TCombobox", fieldbackground=[('readonly', '#313244')], foreground=[('readonly', '#ffffff')])
        self.style.configure("Primary.TButton", font=("Segoe UI", 11, "bold"), background="#00b4d8", foreground="#000000", padding=10, borderwidth=0)
        self.style.map("Primary.TButton", background=[('active', '#90e0ef')])
        self.style.configure("Secondary.TButton", font=("Segoe UI", 9), background="#45475a", foreground="#ffffff", padding=6, borderwidth=0)
        self.style.map("Secondary.TButton", background=[('active', '#585b70')])
        self.style.configure("TProgressbar", thickness=8, troughcolor="#313244", background=self.COLOR_ACCENT)

    def _criar_campo_combo(self, parent, label_text, values, default_val):
        ttk.Label(parent, text=label_text, style="FieldLabel.TLabel").pack(anchor="w", pady=(5, 2))
        cb = ttk.Combobox(parent, state="readonly", font=("Segoe UI", 10), values=values)
        cb.set(default_val)
        cb.pack(fill="x", pady=(0, 12))
        return cb

    def _criar_check(self, parent, text, default_val):
        var = tk.BooleanVar(value=default_val)
        chk = tk.Checkbutton(
            parent, text=text, variable=var, bg=self.COLOR_CARD, fg=self.COLOR_TEXT,
            selectcolor=self.COLOR_BG, activebackground=self.COLOR_CARD, activeforeground=self.COLOR_TEXT, font=("Segoe UI", 9)
        )
        chk.pack(anchor="w", pady=2)
        return var

    def _construir_interface(self):
        top_frame = tk.Frame(self, bg=self.COLOR_BG, pady=15, padx=25)
        top_frame.pack(fill="x")
        ttk.Label(top_frame, text="🧠 Recomendador Inteligente de Linguagens", style="Header.TLabel").pack(anchor="w")
        ttk.Label(top_frame, text="Sistema especialista baseado em inferência de regras para escolha de stack tecnológica.", style="SubHeader.TLabel").pack(anchor="w")

        main_container = tk.Frame(self, bg=self.COLOR_BG, padx=25, pady=10)
        main_container.pack(fill="both", expand=True)
        main_container.columnconfigure(0, weight=1, uniform="group1")
        main_container.columnconfigure(1, weight=1, uniform="group1")
        main_container.rowconfigure(0, weight=1)

        left_card = tk.Frame(main_container, bg=self.COLOR_CARD, highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1, padx=20, pady=20)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ttk.Label(left_card, text="⚙️ Parâmetros do Projeto", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 15))

        self.cb_area = self._criar_campo_combo(left_card, "Qual o objetivo principal do projeto?", [
            "Inteligência Artificial / Ciência de Dados", "Desenvolvimento Web (Fullstack/Backend)",
            "Aplicativos Mobile (Android/iOS)", "Sistemas de Baixo Nível / Performance",
            "Desenvolvimento de Jogos", "Automação / Scripts / Ferramentas CLI"
        ], "Inteligência Artificial / Ciência de Dados")

        self.cb_nivel = self._criar_campo_combo(left_card, "Nível de experiência do desenvolvedor:", [
            "Iniciante (Pouca ou nenhuma bagagem)", "Intermediário (Conhece lógica e sintaxe)", "Avançado (Domina arquitetura e algoritmos)"
        ], "Iniciante (Pouca ou nenhuma bagagem)")

        self.cb_prioridade = self._criar_campo_combo(left_card, "Qual o requisito mais crítico?", [
            "Facilidade de Aprendizado", "Velocidade de Desenvolvimento", "Performance Extrema & Baixa Latência", "Alta Demanda no Mercado de Trabalho"
        ], "Facilidade de Aprendizado")

        self.cb_prazo = self._criar_campo_combo(left_card, "Prazo disponível:", [
            "Curto (MVP ou entrega urgente)", "Médio (Alguns meses de desenvolvimento)", "Longo (Projeto de grande porte)"
        ], "Curto (MVP ou entrega urgente)")

        self.var_multi = self._criar_check(left_card, "Requer suporte Multiplataforma (Windows, Linux, Mac, Web)", True)
        self.var_equipe = self._criar_check(left_card, "Desenvolvimento em equipe/time expandido", False)

        btn_box = tk.Frame(left_card, bg=self.COLOR_CARD)
        btn_box.pack(fill="x", side="bottom", pady=(15, 0))
        self.btn_analisar = ttk.Button(btn_box, text="⚡ Processar Recomendação", style="Primary.TButton", command=self._iniciar_analise)
        self.btn_analisar.pack(fill="x", pady=(0, 5))
        self.btn_limpar = ttk.Button(btn_box, text="🔄 Resetar", style="Secondary.TButton", command=self._resetar_campos)
        self.btn_limpar.pack(fill="x")

        self.right_card = tk.Frame(main_container, bg=self.COLOR_CARD, highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1, padx=20, pady=20)
        self.right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ttk.Label(self.right_card, text="🎯 Resultado da Inferência", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))

        self.progress = ttk.Progressbar(self.right_card, style="TProgressbar", mode="indeterminate")
        self.res_container = tk.Frame(self.right_card, bg=self.COLOR_CARD)
        self.res_container.pack(fill="both", expand=True)
        self._exibir_estado_inicial()

    def _exibir_estado_inicial(self):
        for widget in self.res_container.winfo_children():
            widget.destroy()
        tk.Label(
            self.res_container,
            text="Preencha os parâmetros à esquerda e clique em\n'Processar Recomendação' para gerar o diagnóstico.",
            font=("Segoe UI", 11, "italic"), bg=self.COLOR_CARD, fg=self.COLOR_TEXT_MUTED, justify="center"
        ).pack(expand=True)

    def _resetar_campos(self):
        self._stream_id += 1
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_analisar.config(state="normal")
        self.cb_area.current(0)
        self.cb_nivel.current(0)
        self.cb_prioridade.current(0)
        self.cb_prazo.current(0)
        self.var_multi.set(True)
        self.var_equipe.set(False)
        self._exibir_estado_inicial()

    def _iniciar_analise(self):
        self._stream_id += 1
        self.btn_analisar.config(state="disabled")
        self.progress.pack(fill="x", pady=(0, 15))
        self.progress.start(10)
        threading.Thread(target=self._executar_inferencia_async, daemon=True).start()

    def _executar_inferencia_async(self):
        time.sleep(0.5)
        mapas = {
            "area": {
                "Inteligência Artificial / Ciência de Dados": "ia_data", "Desenvolvimento Web (Fullstack/Backend)": "web",
                "Aplicativos Mobile (Android/iOS)": "mobile", "Sistemas de Baixo Nível / Performance": "sistemas",
                "Desenvolvimento de Jogos": "jogos", "Automação / Scripts / Ferramentas CLI": "automacao"
            },
            "nivel": {
                "Iniciante (Pouca ou nenhuma bagagem)": "iniciante", "Intermediário (Conhece lógica e sintaxe)": "intermediario",
                "Avançado (Domina arquitetura e algoritmos)": "avancado"
            },
            "prio": {
                "Facilidade de Aprendizado": "aprendizado", "Velocidade de Desenvolvimento": "velocidade_dev",
                "Performance Extrema & Baixa Latência": "performance", "Alta Demanda no Mercado de Trabalho": "mercado"
            },
            "prazo": {
                "Curto (MVP ou entrega urgente)": "curto", "Médio (Alguns meses de desenvolvimento)": "medio",
                "Longo (Projeto de grande porte)": "longo"
            }
        }
        ctx = Contexto(
            area=mapas["area"].get(self.cb_area.get(), "ia_data"),
            nivel=mapas["nivel"].get(self.cb_nivel.get(), "iniciante"),
            prioridade=mapas["prio"].get(self.cb_prioridade.get(), "aprendizado"),
            prazo=mapas["prazo"].get(self.cb_prazo.get(), "curto"),
            multiplataforma=self.var_multi.get(),
            trabalho_equipe=self.var_equipe.get()
        )
        resultado = self.motor.analisar(ctx)
        self.after(0, lambda: self._iniciar_streaming_resultado(resultado, self._stream_id))

    def _gerar_efeito_digitacao(self, widget: tk.Label, texto: str, delay: int = 25, chunk_size: int = 1):
        for i in range(chunk_size, len(texto) + chunk_size, chunk_size):
            widget.config(text=texto[:i] + "▌")
            yield delay
        widget.config(text=texto)

    def _iniciar_streaming_resultado(self, res: Resultado, stream_id: int):
        if stream_id != self._stream_id:
            return
        self.progress.stop()
        self.progress.pack_forget()
        for widget in self.res_container.winfo_children():
            widget.destroy()

        def stream_generator():
            box_destaque = tk.Frame(self.res_container, bg="#1e1e2e", padx=15, pady=12, highlightbackground=self.COLOR_ACCENT, highlightthickness=1)
            box_destaque.pack(fill="x", pady=(0, 12))

            lbl_top_lang = tk.Label(box_destaque, text="", font=("Segoe UI", 16, "bold"), bg="#1e1e2e", fg=self.COLOR_ACCENT, justify="left", wraplength=430)
            lbl_top_lang.pack(anchor="w", fill="x")
            yield from self._gerar_efeito_digitacao(lbl_top_lang, f"Recomendação: {res.linguagem_principal}", delay=35)

            lbl_info = tk.Label(box_destaque, text="", font=("Segoe UI", 9), bg="#1e1e2e", fg=self.COLOR_TEXT_MUTED, justify="left", wraplength=430)
            lbl_info.pack(anchor="w", fill="x", pady=(2, 5))
            yield from self._gerar_efeito_digitacao(lbl_info, res.info_texto, delay=20)

            box_sub = tk.Frame(box_destaque, bg="#1e1e2e")
            box_sub.pack(fill="x")
            lbl_conf = tk.Label(box_sub, text="", font=("Segoe UI", 9, "bold"), bg="#1e1e2e", fg=self.COLOR_SUCCESS)
            lbl_conf.pack(side="left")
            yield from self._gerar_efeito_digitacao(lbl_conf, f"Confiança da IA: {res.confianca:.1f}%", delay=25)

            lbl_sec = tk.Label(box_sub, text="", font=("Segoe UI", 9), bg="#1e1e2e", fg=self.COLOR_PURPLE)
            lbl_sec.pack(side="right")
            yield from self._gerar_efeito_digitacao(lbl_sec, f"2ª Opção: {res.linguagem_secundaria}", delay=25)

            lbl_tit_razoes = tk.Label(self.res_container, text="✅ Por que essa linguagem?", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_TEXT)
            lbl_tit_razoes.pack(anchor="w", pady=(5, 2))
            yield 150

            frame_razoes = tk.Frame(self.res_container, bg=self.COLOR_CARD)
            frame_razoes.pack(fill="x", pady=(0, 10))
            for r in res.razoes:
                r_box = tk.Frame(frame_razoes, bg=self.COLOR_CARD)
                r_box.pack(fill="x", anchor="w", pady=1)
                tk.Label(r_box, text="•", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_ACCENT).pack(side="left", padx=(0, 5))
                lbl_r = tk.Label(r_box, text="", font=("Segoe UI", 9), bg=self.COLOR_CARD, fg=self.COLOR_TEXT, justify="left", wraplength=420)
                lbl_r.pack(side="left", anchor="w")
                yield from self._gerar_efeito_digitacao(lbl_r, r, delay=22)
                yield 100

            if res.alertas:
                lbl_tit_alertas = tk.Label(self.res_container, text="⚠️ Pontos de Atenção", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_WARNING)
                lbl_tit_alertas.pack(anchor="w", pady=(5, 2))
                yield 150
                frame_alertas = tk.Frame(self.res_container, bg=self.COLOR_CARD)
                frame_alertas.pack(fill="x", pady=(0, 10))
                for a in res.alertas:
                    a_box = tk.Frame(frame_alertas, bg=self.COLOR_CARD)
                    a_box.pack(fill="x", anchor="w", pady=1)
                    tk.Label(a_box, text="!", font=("Segoe UI", 9, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_WARNING).pack(side="left", padx=(0, 6))
                    lbl_a = tk.Label(a_box, text="", font=("Segoe UI", 9), bg=self.COLOR_CARD, fg=self.COLOR_TEXT, justify="left", wraplength=420)
                    lbl_a.pack(side="left", anchor="w")
                    yield from self._gerar_efeito_digitacao(lbl_a, a, delay=22)
                    yield 100

            lbl_tit_fw = tk.Label(self.res_container, text="🛠️ Ecossistema & Frameworks Sugeridos", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_PURPLE)
            lbl_tit_fw.pack(anchor="w", pady=(5, 2))
            yield 150

            box_fw = tk.Frame(self.res_container, bg="#1e1e2e", padx=10, pady=8)
            box_fw.pack(fill="x", pady=(2, 0))
            lbl_fw = tk.Label(box_fw, text="", font=("Segoe UI", 9, "bold"), bg="#1e1e2e", fg=self.COLOR_TEXT, justify="left", wraplength=430)
            lbl_fw.pack(anchor="w", fill="x")
            yield from self._gerar_efeito_digitacao(lbl_fw, " | ".join(res.frameworks), delay=25)

        gen = stream_generator()
        self._avancar_stream(gen, stream_id)

    def _avancar_stream(self, gen, stream_id: int):
        if stream_id != self._stream_id:
            return
        try:
            delay = next(gen)
            self.after(delay, lambda: self._avancar_stream(gen, stream_id))
        except StopIteration:
            self.btn_analisar.config(state="normal")

if __name__ == "__main__":
    app = AppRecomendadorLinguagem()
    app.mainloop()