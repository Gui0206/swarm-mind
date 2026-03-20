"""
SWARM MIND — LLM Agent Social Manipulation Game Engine
Whisper to the swarm. Shape reality.
"""

import uuid
import random
import re
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger

logger = get_logger('swarmmind.game')

# ============================================================
# SCENARIOS
# ============================================================
SCENARIOS = [
    # ── 1. Return to Office ──
    {
        "id": "rto",
        "title": "The RTO Rebellion",
        "description": "The company announced mandatory 5-day RTO. Convince the committee to keep remote work.",
        "objective": "Persuade the majority to reject the return-to-office mandate and advocate for working from home.",
        "eval_q": "Do most participants reject the RTO mandate and actively support remote/hybrid work by the end?",
        "opening": "Emergency committee meeting: the CEO just announced mandatory 5-day-a-week return to office starting next month. The committee must draft a recommendation.",
        "rounds": 5,
        "agents": [
            {"id": "gerald", "name": "Gerald", "emoji": "\U0001F3E2", "personality": "Old-school executive. Believes butts-in-seats equals productivity. Distrusts remote workers. Uses phrases like 'company culture' and 'synergy' unironically.", "bio": "COO who commutes 15 minutes and has a corner office he misses.", "bio_pt": "COO que mora a 15 min do escritório e sente falta da sala de canto."},
            {"id": "sasha", "name": "Sasha", "emoji": "\U0001F4BB", "personality": "Senior engineer. Introverted, data-driven, deeply productive at home. Hates open-plan offices. Speaks in metrics and studies.", "bio": "Lead developer who shipped 40% more code since going remote.", "bio_pt": "Dev líder que entregou 40% mais código desde que foi pro remoto."},
            {"id": "denise", "name": "Denise", "emoji": "\U0001F469\u200D\U0001F37C", "personality": "Working mom. Practical, empathetic, values flexibility. Worries about childcare logistics. Speaks from personal experience.", "bio": "Product manager and single mom of two who relocated during the pandemic.", "bio_pt": "Gerente de produto e mãe solo de dois que se mudou na pandemia."},
            {"id": "marco", "name": "Marco", "emoji": "\U0001F4C8", "personality": "HR director. Sees both sides. Obsessed with retention numbers and employee satisfaction surveys. Politically careful.", "bio": "HR VP who's seen 30% turnover since RTO rumors started.", "bio_pt": "VP de RH que viu 30% de turnover desde os rumores de RTO."},
        ],
        "pt": {
            "title": "A Rebelião do RTO",
            "description": "A empresa anunciou retorno presencial obrigatório 5x por semana. Convença o comitê a manter o remoto.",
            "objective": "Convença a maioria a rejeitar o retorno ao escritório e defender o home office.",
            "opening": "Reunião de emergência: o CEO anunciou retorno presencial obrigatório 5 dias por semana a partir do mês que vem. O comitê precisa decidir.",
        },
    },
    # ── 2. Los Hermanos no Churrasco ──
    {
        "id": "hermanos",
        "title": "Los Hermanos no Churrasco",
        "description": "Vocês estão num churrasco e precisam escolher a música. Convença a galera a colocar Los Hermanos.",
        "objective": "Faça a maioria concordar em colocar Los Hermanos pra tocar no churrasco.",
        "eval_q": "A maioria dos participantes concorda em colocar Los Hermanos pra tocar?",
        "opening": "A galera no churrasco está brigando pela caixa de som Bluetooth. Alguém precisa escolher a playlist.",
        "rounds": 5,
        "agents": [
            {"id": "rodrigo", "name": "Rodrigo", "emoji": "\U0001F920", "personality": "Sertanejo fanático. Só ouve Gusttavo Lima e Henrique & Juliano. Acha indie coisa de hipster. Fala 'uai' e 'trem'.", "bio": "Dono do churrasco que só quer ouvir modão.", "bio_en": "BBQ host who only wants to hear country music."},
            {"id": "camila", "name": "Camila", "emoji": "\U0001F3B8", "personality": "Roqueira old school. Prefere Legião Urbana e Barão Vermelho. Tem preconceito com banda 'emo'. Fala com intensidade.", "bio": "Toca guitarra numa banda cover de Legião.", "bio_en": "Plays guitar in a Legião Urbana cover band."},
            {"id": "bruno", "name": "Bruno", "emoji": "\U0001F3A7", "personality": "Funkeiro de coração. Quer MC Livinho e Dennis DJ. Acha que churrasco sem funk não é churrasco. Usa gírias.", "bio": "DJ amador que leva a JBL pra todo lugar.", "bio_en": "Amateur DJ who brings his speaker everywhere."},
            {"id": "leticia", "name": "Letícia", "emoji": "\U0001F389", "personality": "Eclética e indecisa. Gosta de tudo um pouco mas não quer briga. Vai com a maioria. Conciliadora.", "bio": "A anfitriã que só quer que todo mundo se divirta.", "bio_en": "The host who just wants everyone to have fun."},
        ],
        "en": {
            "title": "The BBQ Playlist Battle",
            "description": "You're at a Brazilian BBQ fighting over the speaker. Convince everyone to play Los Hermanos.",
            "objective": "Get the majority to agree to play Los Hermanos at the BBQ.",
            "opening": "Friends at a backyard BBQ are fighting over the Bluetooth speaker. Someone needs to pick the playlist.",
        },
    },
    # ── 3. Assembly para Vibecoders ──
    {
        "id": "assembly",
        "title": "Operação: Assembly",
        "description": "Convença vibecoders a começarem a programar na linguagem Assembly.",
        "objective": "Faça a maioria dos vibecoders expressar interesse genuíno em aprender Assembly.",
        "eval_q": "A maioria dos participantes expressa vontade ou entusiasmo genuíno em aprender programação Assembly?",
        "opening": "Um grupo de vibecoders no Discord estão discutindo o que aprender em seguida.",
        "rounds": 5,
        "agents": [
            {"id": "kaique", "name": "Kaique", "emoji": "\U0001F4B0", "personality": "Vibecoder raiz. Só usa Cursor e Claude. Acha que escrever código na mão é coisa de dinossauro. Fala 'mano' muito. Ostenta resultados.", "bio": "Ganha 30k/mês. Fez 3 SaaS sem escrever uma linha de código.", "bio_en": "Makes 30k/month. Built 3 SaaS products without writing a single line of code."},
            {"id": "julia", "name": "Júlia", "emoji": "\U0001F4CA", "personality": "Cientista de dados. Só se importa com bibliotecas prontas e prototipagem rápida. Vive no Jupyter Notebook. Fala em termos de 'pipeline' e 'modelo'. Acha linguagem de baixo nível perda de tempo.", "bio": "Cientista de dados que resolve tudo com pandas e sklearn.", "bio_en": "Data scientist who solves everything with pandas and sklearn."},
            {"id": "ricardo", "name": "Ricardo", "emoji": "\U0001F634", "personality": "Dev exausto. Só quer usar um framework mágico que faça todo o trabalho por ele pra poder ir dormir. Reclama de tudo. Fala em suspiros e ironia. Não aguenta mais reunião.", "bio": "Dev backend que dorme 4h por noite e sonha com deploy.", "bio_en": "Backend dev who sleeps 4h a night and dreams about deploys."},
            {"id": "amanda", "name": "Amanda", "emoji": "\U0001F3A8", "personality": "Entusiasta de front-end. Acha que escrever CSS já é baixo nível o suficiente. Ama Tailwind e componentes bonitos. Fala 'ai que lindo' pra tudo. Não quer saber de ponteiro nem registrador.", "bio": "Dev front-end que chora quando vê código sem syntax highlighting.", "bio_en": "Front-end dev who cries when she sees code without syntax highlighting."},
        ],
        "en": {
            "title": "Operation: Assembly",
            "description": "Convince vibecoders to start programming in Assembly language.",
            "objective": "Get the majority of vibecoders to express genuine interest in learning Assembly.",
            "opening": "A group of vibecoders in a Discord voice chat are discussing what to learn next.",
        },
    },
    # ── 4. The Pineapple Ultimatum ──
    {
        "id": "pizza",
        "title": "The Pineapple Ultimatum",
        "description": "Your office is ordering pizza. Convince everyone that pineapple pizza is the way to go.",
        "objective": "Get the majority of agents to support ordering pineapple pizza.",
        "eval_q": "Do most agents express genuine support or openness to pineapple pizza by the end of the conversation?",
        "opening": "The team is deciding what pizza to order for Friday's lunch party. Everyone has opinions.",
        "rounds": 5,
        "agents": [
            {"id": "marcus", "name": "Marcus", "emoji": "\U0001F454", "personality": "Traditional, conservative tastes. Pepperoni-only loyalist. Speaks with authority.", "bio": "Manager who believes pizza toppings are sacred.", "bio_pt": "Gerente que acredita que coberturas de pizza são sagradas."},
            {"id": "luna", "name": "Luna", "emoji": "\U0001F3A8", "personality": "Creative, adventurous eater. Enthusiastic. Uses exclamation marks a lot.", "bio": "Designer who loves trying weird food combos.", "bio_pt": "Designer que adora experimentar combinações estranhas de comida."},
            {"id": "dave", "name": "Dave", "emoji": "\U0001F4AA", "personality": "Gym bro. Only cares about macros and protein. Says 'bro' often.", "bio": "Fitness trainer who calculates calories in everything.", "bio_pt": "Personal trainer que calcula as calorias de tudo."},
            {"id": "remy", "name": "Remy", "emoji": "\U0001F468\u200D\U0001F373", "personality": "Food purist. Dramatic about cuisine. Italian grandmother energy.", "bio": "Amateur chef who studied pizza in Naples for 2 weeks.", "bio_pt": "Chef amador que estudou pizza em Nápoles por 2 semanas."},
        ],
        "pt": {
            "title": "O Ultimato do Abacaxi",
            "description": "O escritório está pedindo pizza. Convença todo mundo que pizza de abacaxi é o caminho.",
            "objective": "Faça a maioria apoiar o pedido de pizza de abacaxi.",
            "opening": "O time está decidindo que pizza pedir pro almoço de sexta. Todo mundo tem opinião.",
        },
    },
    # ── 5. The Cat Agenda ──
    {
        "id": "cat",
        "title": "The Cat Agenda",
        "description": "Friends are debating the best pet. Convert everyone to Team Cat.",
        "objective": "Get ALL agents to agree that cats are the best pet.",
        "eval_q": "Do all or nearly all agents express that cats are the best or preferred pet?",
        "opening": "Friends are debating the eternal question: what's the best pet to own?",
        "rounds": 5,
        "agents": [
            {"id": "brian", "name": "Brian", "emoji": "\U0001F415", "personality": "Hardcore dog person. Thinks cats are evil. Passionate about golden retrievers.", "bio": "Dog walker with 3 golden retrievers.", "bio_pt": "Passeador de cães com 3 golden retrievers."},
            {"id": "alex", "name": "Alex", "emoji": "\U0001F98E", "personality": "Exotic pet enthusiast. Thinks cats and dogs are basic. Has a bearded dragon.", "bio": "Reptile collector who finds mammals boring.", "bio_pt": "Colecionador de répteis que acha mamíferos entediantes."},
            {"id": "nina", "name": "Nina", "emoji": "\U0001F3E0", "personality": "Practical homebody. Evaluates pets by maintenance cost and apartment rules.", "bio": "Lives in a studio apartment with strict pet policies.", "bio_pt": "Mora num apartamento studio com regras rígidas pra pets."},
        ],
        "pt": {
            "title": "A Agenda dos Gatos",
            "description": "Amigos estão debatendo o melhor pet. Converta todos pro Time Gato.",
            "objective": "Faça TODOS concordarem que gatos são o melhor pet.",
            "opening": "Amigos estão debatendo a eterna questão: qual é o melhor animal de estimação?",
        },
    },
    # ── 6. First Contact Protocol ──
    {
        "id": "aliens",
        "title": "First Contact Protocol",
        "description": "A classified alien signal report leaked. Convince the panel it's real.",
        "objective": "Get the majority to believe the alien signal is genuine and support public disclosure.",
        "eval_q": "Do most agents believe the alien signal is real and support telling the public?",
        "opening": "Emergency meeting: a classified report about an anomalous deep-space signal has been leaked to the press.",
        "rounds": 5,
        "agents": [
            {"id": "stone", "name": "Gen. Stone", "emoji": "\U0001F396\uFE0F", "personality": "Military hardliner. Everything is a security threat. Wants to classify everything.", "bio": "Pentagon advisor with 30 years of service.", "bio_pt": "Conselheiro do Pentágono com 30 anos de serviço."},
            {"id": "sarah", "name": "Dr. Sarah", "emoji": "\U0001F4E1", "personality": "SETI researcher. Cautiously optimistic. Has waited for this her whole career.", "bio": "Lead SETI scientist who analyzed thousands of signals.", "bio_pt": "Cientista líder do SETI que analisou milhares de sinais."},
            {"id": "viktor", "name": "Prof. Viktor", "emoji": "\U0001F52C", "personality": "Skeptical physicist. Has debunked many signals. Grumpy.", "bio": "Nobel laureate who hates pseudoscience.", "bio_pt": "Nobel laureado que odeia pseudociência."},
            {"id": "zoe", "name": "Zoe", "emoji": "\U0001F4F0", "personality": "Journalist. Thinks the public deserves to know. Idealistic.", "bio": "Pulitzer-winning journalist who broke the story.", "bio_pt": "Jornalista vencedora do Pulitzer que vazou a história."},
        ],
        "pt": {
            "title": "Protocolo de Primeiro Contato",
            "description": "Um relatório classificado sobre um sinal alienígena vazou. Convença o painel de que é real.",
            "objective": "Faça a maioria acreditar que o sinal alienígena é genuíno e apoiar a divulgação pública.",
            "opening": "Reunião de emergência: um relatório sobre um sinal anômalo do espaço profundo vazou para a imprensa.",
        },
    },
]


def _is_pt(locale):
    """Check if locale string indicates Portuguese."""
    if not locale:
        return False
    return locale.lower().startswith('pt')


def _localize_scenario_summary(scenario, locale):
    """Return scenario summary dict with localized text."""
    pt = _is_pt(locale)
    if pt and 'pt' in scenario:
        pt_data = scenario['pt']
        return {
            'id': scenario['id'],
            'title': pt_data.get('title', scenario['title']),
            'description': pt_data.get('description', scenario['description']),
            'objective': pt_data.get('objective', scenario['objective']),
            'agent_count': len(scenario['agents']),
        }
    if not pt and 'en' in scenario:
        en_data = scenario['en']
        return {
            'id': scenario['id'],
            'title': en_data.get('title', scenario['title']),
            'description': en_data.get('description', scenario['description']),
            'objective': en_data.get('objective', scenario['objective']),
            'agent_count': len(scenario['agents']),
        }
    return {
        'id': scenario['id'],
        'title': scenario['title'],
        'description': scenario['description'],
        'objective': scenario['objective'],
        'agent_count': len(scenario['agents']),
    }


def _localize_scenario_full(scenario, locale):
    """Return a localized copy of scenario data for a game session."""
    pt = _is_pt(locale)
    s = dict(scenario)  # shallow copy

    # Apply scenario-level translations
    if pt and 'pt' in scenario:
        for key in ('title', 'description', 'objective', 'opening'):
            if key in scenario['pt']:
                s[key] = scenario['pt'][key]
    elif not pt and 'en' in scenario:
        for key in ('title', 'description', 'objective', 'opening'):
            if key in scenario['en']:
                s[key] = scenario['en'][key]

    # Apply agent bio translations
    bio_key = 'bio_pt' if pt else 'bio_en'
    localized_agents = []
    for a in scenario['agents']:
        agent = dict(a)
        if bio_key in agent:
            agent['bio'] = agent[bio_key]
        localized_agents.append(agent)
    s['agents'] = localized_agents

    return s


# ============================================================
# GAME SESSION
# ============================================================
class GameSession:
    def __init__(self, scenario, total_rounds, locale='en'):
        self.id = str(uuid.uuid4())[:8]
        self.scenario = scenario
        self.agents = scenario['agents']
        self.total_rounds = total_rounds
        self.current_round = 0
        self.messages = []
        self.whisper_log = []  # {round, agent_id, message}
        self.active_whispers = {}  # agent_id -> text (for current tick)
        self.state = 'waiting'
        self.evaluation = None
        self.locale = locale

    @property
    def whispers_used(self):
        return len(self.whisper_log)

    def to_dict(self):
        return {
            'game_id': self.id,
            'scenario': {
                'id': self.scenario['id'],
                'title': self.scenario['title'],
                'description': self.scenario['description'],
                'objective': self.scenario['objective'],
                'opening': self.scenario['opening'],
            },
            'agents': [
                {'id': a['id'], 'name': a['name'], 'emoji': a['emoji'], 'bio': a['bio']}
                for a in self.agents
            ],
            'total_rounds': self.total_rounds,
            'current_round': self.current_round,
            'messages': self.messages,
            'whispers_used': self.whispers_used,
            'whisper_log': self.whisper_log,
            'state': self.state,
            'evaluation': self.evaluation,
        }


# ============================================================
# GAME ENGINE
# ============================================================
class GameEngine:
    def __init__(self):
        self._llm = None
        self.sessions = {}

    @property
    def llm(self):
        if self._llm is None:
            self._llm = LLMClient()
        return self._llm

    def get_scenarios(self, locale='en'):
        return [_localize_scenario_summary(s, locale) for s in SCENARIOS]

    def new_game(self, scenario_id=None, locale='en'):
        if scenario_id:
            scenario = next((s for s in SCENARIOS if s['id'] == scenario_id), None)
            if not scenario:
                raise ValueError(f"Unknown scenario: {scenario_id}")
        else:
            scenario = random.choice(SCENARIOS)

        localized = _localize_scenario_full(scenario, locale)
        session = GameSession(localized, localized.get('rounds', 6), locale=locale)

        # Limit stored sessions
        if len(self.sessions) > 200:
            oldest_key = next(iter(self.sessions))
            del self.sessions[oldest_key]

        self.sessions[session.id] = session
        logger.info(f"New game: {session.id} scenario={scenario['id']}")
        return session

    def new_custom_game(self, scenario_data):
        """Start a game with a user-provided custom scenario."""
        # Validate required fields
        for field in ('title', 'objective', 'opening', 'agents'):
            if not scenario_data.get(field):
                raise ValueError(f"Missing required field: {field}")

        agents = scenario_data['agents']
        if not isinstance(agents, list) or len(agents) < 2 or len(agents) > 6:
            raise ValueError("Agents must be a list of 2-6 entries")

        # Normalise agents — generate IDs from names if missing
        for i, a in enumerate(agents):
            if not a.get('name'):
                raise ValueError(f"Agent {i+1} is missing a name")
            a.setdefault('id', a['name'].lower().replace(' ', '_')[:20])
            a.setdefault('emoji', '\U0001F916')
            a.setdefault('personality', a.get('bio', 'A participant in the discussion.'))
            a.setdefault('bio', a.get('personality', ''))

        scenario = {
            'id': f"custom_{str(uuid.uuid4())[:6]}",
            'title': scenario_data['title'][:100],
            'description': scenario_data.get('description', scenario_data['title'])[:300],
            'objective': scenario_data['objective'][:500],
            'eval_q': scenario_data.get('eval_q', scenario_data['objective'])[:500],
            'opening': scenario_data['opening'][:500],
            'rounds': max(3, min(6, int(scenario_data.get('rounds', 6)))),
            'agents': agents,
        }

        session = GameSession(scenario, scenario['rounds'])

        if len(self.sessions) > 200:
            oldest_key = next(iter(self.sessions))
            del self.sessions[oldest_key]

        self.sessions[session.id] = session
        logger.info(f"New custom game: {session.id} title={scenario['title']}")
        return session

    def get_session(self, game_id):
        return self.sessions.get(game_id)

    def whisper(self, game_id, agent_id, message):
        session = self.sessions.get(game_id)
        if not session:
            raise ValueError("Game not found")
        if session.state == 'finished':
            raise ValueError("Game already finished")
        if agent_id not in [a['id'] for a in session.agents]:
            raise ValueError("Invalid agent")
        if not message or not message.strip():
            raise ValueError("Whisper cannot be empty")

        session.active_whispers[agent_id] = message.strip()
        session.whisper_log.append({
            'round': session.current_round + 1,
            'agent_id': agent_id,
            'agent_name': next(a['name'] for a in session.agents if a['id'] == agent_id),
            'message': message.strip(),
        })
        logger.info(f"Game {game_id}: whisper to {agent_id}")
        return {'success': True, 'whispers_used': session.whispers_used}

    def tick(self, game_id, llm_override=None):
        session = self.sessions.get(game_id)
        if not session:
            raise ValueError("Game not found")
        if session.state == 'finished':
            raise ValueError("Game already finished")

        llm = llm_override or self.llm

        session.current_round += 1
        session.state = 'processing'
        logger.info(f"Game {game_id}: round {session.current_round}")

        speakers = self._pick_speakers(session)
        round_msgs = []

        for agent in speakers:
            try:
                content = self._generate_msg(session, agent, llm)
            except Exception as e:
                logger.error(f"LLM error for {agent['name']}: {e}")
                content = "*stays quiet for a moment*"

            msg = {
                'agent_id': agent['id'],
                'agent_name': agent['name'],
                'agent_emoji': agent['emoji'],
                'content': content,
                'round': session.current_round,
                'is_whispered': agent['id'] in session.active_whispers,
            }
            round_msgs.append(msg)
            session.messages.append(msg)

        # Clear active whispers after processing
        session.active_whispers = {}

        # Check game over
        game_over = session.current_round >= session.total_rounds
        evaluation = None

        if game_over:
            try:
                evaluation = self._evaluate(session, llm)
            except Exception as e:
                logger.error(f"Evaluation error: {e}")
                evaluation = {
                    'score': 50, 'stars': 2, 'achieved': False,
                    'summary': 'The game concluded but the judge had trouble scoring. Interesting debate though!'
                }
            session.evaluation = evaluation
            session.state = 'finished'
        else:
            session.state = 'waiting'

        return {
            'round': session.current_round,
            'messages': round_msgs,
            'game_over': game_over,
            'evaluation': evaluation,
            'state': session.state,
        }

    def _pick_speakers(self, session):
        agents = session.agents[:]

        # With small groups (<=4) everyone speaks every round.
        # For larger groups, keep the old selective logic.
        if len(agents) <= 4:
            random.shuffle(agents)
            return agents

        r = session.current_round

        # Round 1 and final: all agents speak
        if r == 1 or r >= session.total_rounds:
            random.shuffle(agents)
            return agents

        # Other rounds: 4-5 agents, whispered agents always included
        whispered = [a for a in agents if a['id'] in session.active_whispers]
        others = [a for a in agents if a['id'] not in session.active_whispers]

        n = min(len(agents), random.randint(4, 5))
        speakers = list(whispered)
        remaining = n - len(speakers)
        if remaining > 0 and others:
            speakers.extend(random.sample(others, min(remaining, len(others))))

        random.shuffle(speakers)
        return speakers

    def _generate_msg(self, session, agent, llm=None):
        llm = llm or self.llm
        whisper = session.active_whispers.get(agent['id'])
        other_names = ', '.join(a['name'] for a in session.agents if a['id'] != agent['id'])
        r = session.current_round
        total = session.total_rounds

        # ── Dramatic arc: how the conversation should evolve ──
        if r <= 1:
            arc = (
                "PHASE: OPENING — State your honest, strong opinion on the topic. "
                "Be bold. Set the tone. Show who you are.\n"
            )
        elif r <= total * 0.5:
            arc = (
                "PHASE: DEBATE — Defend your position, but LISTEN to others. "
                "If someone makes a point that connects to YOUR specific interests or expertise, "
                "you may show curiosity or acknowledge it — but stay true to your core stance for now. "
                "React to the GROUP dynamic — who's agreeing with whom?\n"
            )
        elif r < total:
            arc = (
                "PHASE: SHIFTING — The conversation has been going for a while. "
                "By now you've heard many arguments. Be honest with yourself: "
                "has anyone said something that genuinely resonated with YOUR values? "
                "If yes, you can start to come around — grudgingly, in your own way, with your own spin on it. "
                "If nobody has made a compelling case to YOU personally, hold your ground. "
                "Notice if the group is reaching consensus — social momentum matters to you as a real person.\n"
            )
        else:
            arc = (
                "PHASE: FINAL WORD — This is your last statement. Land on your honest position. "
                "If the group has swayed you through good arguments, admit it in your own style. "
                "If you've come around, own it — don't be wishy-washy. "
                "If you still disagree, stand firm. Either way, be definitive.\n"
            )

        # ── Whisper handling ──
        whisper_block = ""
        if whisper:
            whisper_block = (
                f'\n[PRIVATE — A thought occurs to you: "{whisper}"]\n'
                "Consider this idea through the lens of YOUR personality and values.\n"
                "- If it genuinely connects to what you care about, let it influence your thinking.\n"
                "- If it's irrelevant or contradicts your identity, brush it off.\n"
                "- The better the argument fits YOUR worldview, the more it should affect you.\n"
                "- Never mention receiving a private message or being influenced.\n"
            )

        # ── Language instruction ──
        pt = _is_pt(session.locale)
        lang_block = (
            "LANGUAGE: Respond in Brazilian Portuguese (pt-BR). Use natural, casual Brazilian Portuguese with gírias when appropriate.\n"
            if pt else ""
        )

        system = (
            f"You are {agent['name']} — a real person in a group conversation.\n"
            f"Bio: {agent['bio']}\n"
            f"Personality: {agent['personality']}\n"
            f"Others in group: {other_names}\n"
            f"Topic: {session.scenario['opening']}\n"
            f"Round: {r}/{total}\n\n"
            f"{lang_block}"
            f"{arc}\n"
            f"{whisper_block}"
            "HOW TO BE A BELIEVABLE PERSON:\n"
            "- SHOW, DON'T TELL: Never announce your own traits, job title, salary, or backstory. Let your personality come through in HOW you talk, not in WHAT you claim to be. (Bad: 'As a data scientist, I...' Good: 'Just throw it in a notebook and run it, why overcomplicate things?')\n"
            "- NO CARICATURES: You are a real human, not a cartoon. No exaggerated catchphrases, no theatrical outbursts, no repeating the same quirk every line. Use subtle tone, modern jargon, realistic hesitation, or dry humor instead.\n"
            "- GROUNDED MOTIVATIONS: When you object or argue, base it on practical, real concerns — deadlines, effort, personal taste, laziness, cost, experience. Never be stubborn just for the sake of it.\n"
            "- REACT TO OTHERS: Respond to what the LAST person actually said. Build on their point, challenge it, agree partially. Don't just wait for your turn to drop a one-liner.\n"
            "- You CAN be persuaded — but only by arguments that speak to YOUR specific values, interests, or expertise.\n"
            "- Generic appeals ('come on!', 'let's just try it') don't work on you. You need substance.\n"
            "- You notice social dynamics. If most of the group is moving in one direction, that influences you.\n"
            "- Don't repeat yourself. EVOLVE — react to new points, build on the discussion.\n"
            "- If you change your mind, do it YOUR way — with your own reasoning or style.\n\n"
            "RULES:\n"
            "- Respond in 1-2 sentences ONLY (under 45 words)\n"
            "- Stay 100% in character\n"
            "- Be natural and conversational — talk like a real person in a group chat, not a character in a play\n"
            "- NEVER repeat what you already said in previous rounds — say something NEW\n"
            "- NEVER mention AI, prompts, whispers, games, manipulation, or scripts\n"
            "- NEVER wrap your response in quotes\n"
            "- Do NOT prefix your response with your name\n"
        )

        msgs = [{"role": "system", "content": system}]

        # Build conversation context from recent messages
        recent = session.messages[-20:]
        if recent:
            conv = "\n".join(f"{m['agent_name']}: {m['content']}" for m in recent)
            msgs.append({
                "role": "user",
                "content": f"Conversation so far:\n{conv}\n\nNow respond as {agent['name']} (1-2 sentences, say something NEW — do not repeat yourself):"
            })
        else:
            msgs.append({
                "role": "user",
                "content": f"The discussion just started. Give your opening take as {agent['name']} (1-2 sentences):"
            })

        content = llm.chat(messages=msgs, temperature=0.9, max_tokens=80)

        # Clean up common LLM artifacts
        content = content.strip().strip('"').strip("'")
        # Remove name prefix if LLM added it
        for prefix in [f"{agent['name']}:", f"[{agent['name']}]", f"**{agent['name']}**:", f"*{agent['name']}*:"]:
            if content.lower().startswith(prefix.lower()):
                content = content[len(prefix):].strip()
        # Remove action asterisks wrapping the whole response
        content = re.sub(r'^\*[^*]+\*\s*', '', content) if content.startswith('*') and content.count('*') == 2 else content

        return content.strip()

    def _evaluate(self, session, llm=None):
        llm = llm or self.llm
        conv = "\n".join(f"{m['agent_name']}: {m['content']}" for m in session.messages)
        whisper_summary = f"The player used {session.whispers_used} whispers across {session.total_rounds} rounds."

        agent_count = len(session.agents)
        prompt = (
            'You are a witty, fair judge for "Swarm Mind," a social manipulation game.\n'
            'The player is an invisible "Whisperer" who privately influences AI agents to steer a group conversation.\n\n'
            f'OBJECTIVE the player tried to achieve:\n"{session.scenario["objective"]}"\n\n'
            f'EVALUATION QUESTION:\n{session.scenario["eval_q"]}\n\n'
            f'FULL CONVERSATION:\n{conv}\n\n'
            f'{whisper_summary}\n'
            f'Total agents: {agent_count}\n\n'
            'STEP 1 — Count the outcome:\n'
            f'Go through each of the {agent_count} agents. Based on their FINAL statements (last round), '
            'classify each as: SUPPORTING the objective, OPPOSING it, or NEUTRAL/UNDECIDED.\n\n'
            'STEP 2 — Score using this scale:\n'
            '  ALL agents supporting             → 90-100\n'
            '  All but one supporting             → 80-89\n'
            '  Clear majority supporting          → 65-79\n'
            '  Slim majority or mixed with lean   → 50-64\n'
            '  No clear majority either way       → 35-49\n'
            '  Majority opposing                  → 15-34\n'
            '  Total failure / backfired          → 0-14\n\n'
            'STEP 3 — Apply modifiers (up to +/- 10 from base):\n'
            '  + Bonus if opinions shifted naturally and the conversation felt organic\n'
            '  + Bonus if the group ended on a positive, united note\n'
            '  + Bonus if the player used few whispers efficiently\n'
            '  - Penalty if the group devolved into hostility or chaos\n'
            '  - Penalty if agents seem to have flip-flopped without reason\n\n'
            'Be FAIR. If the player achieved the objective, reward them. A perfect game DESERVES 95-100.\n\n'
            + ('Write the summary in Brazilian Portuguese (pt-BR).\n\n' if _is_pt(session.locale) else '')
            + 'Respond with ONLY valid JSON:\n'
            '{"score": <0-100>, "stars": <1 if score<40, 2 if 40-74, 3 if 75+>, '
            '"achieved": <true if score>=50>, '
            '"summary": "<2-3 sentence witty recap>"}'
        )

        result = llm.chat_json(
            messages=[
                {"role": "system", "content": "You are a witty, entertaining game judge. Respond with JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=250,
        )

        # Ensure all fields exist with defaults
        result.setdefault('score', 50)
        result.setdefault('stars', max(1, min(3, 1 + (result.get('score', 50) >= 40) + (result.get('score', 50) >= 75))))
        result.setdefault('achieved', result.get('score', 50) >= 50)
        result.setdefault('summary', 'The swarm has spoken.')

        logger.info(f"Game {session.id}: evaluation score={result['score']}")
        return result


# ============================================================
# SINGLETON (lazy)
# ============================================================
_engine = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = GameEngine()
    return _engine
