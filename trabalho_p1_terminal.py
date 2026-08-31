import sys
from dataclasses import dataclass
from typing import List, Dict
import random

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stdin.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

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

def obter_opcao(prompt, opcoes):
    while True:
        print(f"\n{prompt}")
        for i, (chave, rotulo) in enumerate(opcoes, start=1):
            print(f"  [{i}] {rotulo}")
        escolha = input("\nDigite o número da opção desejada: ").strip()
        if escolha.isdigit():
            idx = int(escolha) - 1
            if 0 <= idx < len(opcoes):
                return opcoes[idx][0]
        print("Opção inválida. Tente novamente.")

def obter_booleano(prompt):
    while True:
        resp = input(f"\n{prompt} (s/n): ").strip().lower()
        if resp in ("s", "sim", "1", "y", "yes"):
            return True
        if resp in ("n", "nao", "não", "0"):
            return False
        print("Resposta inválida. Digite 's' para sim ou 'n' para não.")

def executar():
    print("=" * 65)
    print("SISTEMA ESPECIALISTA: RECOMENDADOR DE LINGUAGEM DE PROGRAMAÇÃO")
    print("=" * 65)
    print("Responda às perguntas abaixo para receber a recomendação ideal.\n")

    opcoes_area = [
        ("ia_data", "Inteligência Artificial / Ciência de Dados"),
        ("web", "Desenvolvimento Web (Fullstack / Backend)"),
        ("mobile", "Aplicativos Mobile (Android / iOS)"),
        ("sistemas", "Sistemas de Baixo Nível / Alta Performance"),
        ("jogos", "Desenvolvimento de Jogos"),
        ("automacao", "Automação / Scripts / Ferramentas CLI")
    ]
    area = obter_opcao("1. Qual é o objetivo principal do seu projeto?", opcoes_area)

    opcoes_nivel = [
        ("iniciante", "Iniciante (Pouca ou nenhuma bagagem na área)"),
        ("intermediario", "Intermediário (Conhece lógica e sintaxe básica)"),
        ("avancado", "Avançado (Domina arquitetura e algoritmos complexos)")
    ]
    nivel = obter_opcao("2. Qual é o seu nível de experiência técnica?", opcoes_nivel)

    opcoes_prioridade = [
        ("aprendizado", "Facilidade e Curva de Aprendizado"),
        ("velocidade_dev", "Velocidade e Produtividade no Desenvolvimento"),
        ("performance", "Performance Extrema e Baixa Latência"),
        ("mercado", "Alta Demanda e Oportunidades no Mercado de Trabalho")
    ]
    prioridade = obter_opcao("3. Qual é o requisito mais crítico para o projeto?", opcoes_prioridade)

    opcoes_prazo = [
        ("curto", "Curto (MVP ou entrega urgente)"),
        ("medio", "Médio (Alguns meses de desenvolvimento)"),
        ("longo", "Longo (Projeto corporativo de grande porte)")
    ]
    prazo = obter_opcao("4. Qual é o prazo disponível para desenvolvimento?", opcoes_prazo)

    multiplataforma = obter_booleano("5. O projeto exige suporte a múltiplas plataformas (Windows, Linux, macOS, Web)?")
    trabalho_equipe = obter_booleano("6. O desenvolvimento será realizado em equipe/time expandido?")

    ctx = Contexto(
        area=area,
        nivel=nivel,
        prioridade=prioridade,
        prazo=prazo,
        multiplataforma=multiplataforma,
        trabalho_equipe=trabalho_equipe
    )

    motor = MotorDecisao()
    resultado = motor.analisar(ctx)

    print("\n" + "=" * 65)
    print("RESULTADO DA RECOMENDAÇÃO")
    print("=" * 65)
    print(f"\n[+] Linguagem Recomendada: {resultado.linguagem_principal}")
    print(f"[+] Nível de Confiança da Decisão: {resultado.confianca:.1f}%")
    print(f"[+] Segunda Melhor Opção: {resultado.linguagem_secundaria}")
    print(f"\nResumo da Stack:\n  {resultado.info_texto}")

    print("\n" + "-" * 65)
    print("POR QUE TOMEI ESSA DECISÃO?")
    print("-" * 65)
    for razao in resultado.razoes:
        print(f" * {razao}")

    if resultado.alertas:
        print("\n" + "-" * 65)
        print("PONTOS DE ATENÇÃO E TRADE-OFFS")
        print("-" * 65)
        for alerta in resultado.alertas:
            print(f" ! {alerta}")

    if resultado.frameworks:
        print("\n" + "-" * 65)
        print("ECOSSISTEMA E FRAMEWORKS SUGERIDOS")
        print("-" * 65)
        print("   " + " | ".join(resultado.frameworks))

    print("\n" + "=" * 65 + "\n")

if __name__ == "__main__":
    executar()
