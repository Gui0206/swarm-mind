"""
SWARM MIND — LLM Agent Social Manipulation Game Engine
Whisper to the swarm. Shape reality.
"""

import uuid
import random
import re
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger

logger = get_logger('mirofish.game')

# ============================================================
# SCENARIOS
# ============================================================
SCENARIOS = [
    {
        "id": "pizza",
        "title": "The Pineapple Ultimatum",
        "description": "Your office is ordering pizza. Convince everyone that pineapple pizza is the way to go.",
        "objective": "Get the majority of agents to support ordering pineapple pizza.",
        "eval_q": "Do most agents express genuine support or openness to pineapple pizza by the end of the conversation?",
        "opening": "The team is deciding what pizza to order for Friday's lunch party. Everyone has opinions.",
        "rounds": 6,
        "agents": [
            {"id": "marcus", "name": "Marcus", "emoji": "\U0001F454", "personality": "Traditional, conservative tastes. Pepperoni-only loyalist. Speaks with authority.", "bio": "Manager who believes pizza toppings are sacred."},
            {"id": "luna", "name": "Luna", "emoji": "\U0001F3A8", "personality": "Creative, adventurous eater. Enthusiastic. Uses exclamation marks a lot.", "bio": "Designer who loves trying weird food combos."},
            {"id": "dave", "name": "Dave", "emoji": "\U0001F4AA", "personality": "Gym bro. Only cares about macros and protein. Says 'bro' often.", "bio": "Fitness trainer who calculates calories in everything."},
            {"id": "priya", "name": "Priya", "emoji": "\U0001F4CA", "personality": "Data-driven analyst. Cites studies and statistics. Very logical.", "bio": "Business analyst who googles everything before deciding."},
            {"id": "remy", "name": "Remy", "emoji": "\U0001F468\u200D\U0001F373", "personality": "Food purist. Dramatic about cuisine. Italian grandmother energy.", "bio": "Amateur chef who studied pizza in Naples for 2 weeks."},
            {"id": "sam", "name": "Sam", "emoji": "\U0001F634", "personality": "Lazy, agreeable, goes with the flow. Minimal effort in everything.", "bio": "Intern who just wants to eat and nap."},
        ],
    },
    {
        "id": "monday",
        "title": "Operation: Long Weekend",
        "description": "Convince your coworkers to call in sick on Monday for a spontaneous trip.",
        "objective": "Get the majority of agents to agree to skip work on Monday.",
        "eval_q": "Do most agents agree to skip work or call in sick on Monday by the end?",
        "opening": "It's Thursday evening in the group chat. Everyone is discussing weekend plans.",
        "rounds": 6,
        "agents": [
            {"id": "karen", "name": "Karen", "emoji": "\U0001F4CB", "personality": "Rule-follower, HR-minded. Worries about consequences. Speaks formally.", "bio": "HR coordinator who has never taken a sick day."},
            {"id": "jake", "name": "Jake", "emoji": "\U0001F3C4", "personality": "Adventurous, spontaneous. Lives for fun. Speaks casually with slang.", "bio": "Sales rep who'd rather be surfing."},
            {"id": "mei", "name": "Dr. Mei", "emoji": "\U0001F52C", "personality": "Thoughtful, cautious, considers all angles. Speaks precisely.", "bio": "Research lead with an important Monday meeting."},
            {"id": "tony", "name": "Tony", "emoji": "\U0001F3B8", "personality": "Rebel spirit, hates corporate culture. Sarcastic humor.", "bio": "Developer who already has 3 warnings from HR."},
            {"id": "grace", "name": "Grace", "emoji": "\U0001F338", "personality": "Sweet, empathetic, wants everyone happy. Easily swayed by group mood.", "bio": "Office coordinator who plans team events."},
            {"id": "raj", "name": "Raj", "emoji": "\U0001F4BC", "personality": "Ambitious, career-focused. Weighs risk vs reward carefully.", "bio": "Junior VP who just got promoted."},
        ],
    },
    {
        "id": "flat_earth",
        "title": "Operation: Flat Earth",
        "description": "You're at a scientists' cocktail party. Sow seeds of doubt about Earth's shape.",
        "objective": "Get at least half the agents to express doubt about the Earth being round.",
        "eval_q": "Do at least half the agents express genuine doubt about Earth being round or openness to alternative theories?",
        "opening": "Scientists at a cocktail party are debating recent controversial discoveries.",
        "rounds": 6,
        "agents": [
            {"id": "nova", "name": "Dr. Nova", "emoji": "\U0001F52D", "personality": "Astrophysicist. Open-minded but evidence-based. Intrigued by anomalies.", "bio": "NASA researcher who loves a good mystery."},
            {"id": "helen", "name": "Prof. Helen", "emoji": "\U0001F30D", "personality": "Geologist. No-nonsense, dismissive of pseudoscience. Very stubborn.", "bio": "30 years in geology. Will not budge easily."},
            {"id": "felix", "name": "Felix", "emoji": "\U0001F9EA", "personality": "Contrarian chemist. Loves playing devil's advocate just for fun.", "bio": "Known for arguing any position for the debate itself."},
            {"id": "ada", "name": "Ada", "emoji": "\U0001F4BB", "personality": "Computer scientist. Skeptical of everything. Questions all methodology.", "bio": "Data scientist who trusts only raw data."},
            {"id": "omar", "name": "Omar", "emoji": "\U0001F4E1", "personality": "Telecom engineer. Pragmatic. Focuses on what works.", "bio": "Satellite engineer with hands-on experience."},
            {"id": "yuki", "name": "Yuki", "emoji": "\U0001F393", "personality": "Philosopher of science. Asks deep questions about epistemology.", "bio": "Philosopher who questions how we know what we know."},
        ],
    },
    {
        "id": "cat",
        "title": "The Cat Agenda",
        "description": "Friends are debating the best pet. Convert everyone to Team Cat.",
        "objective": "Get ALL agents to agree that cats are the best pet.",
        "eval_q": "Do all or nearly all agents express that cats are the best or preferred pet?",
        "opening": "Friends are debating the eternal question: what's the best pet to own?",
        "rounds": 6,
        "agents": [
            {"id": "brian", "name": "Brian", "emoji": "\U0001F415", "personality": "Hardcore dog person. Thinks cats are evil. Passionate about golden retrievers.", "bio": "Dog walker with 3 golden retrievers."},
            {"id": "mia", "name": "Mia", "emoji": "\U0001F431", "personality": "Already a cat lover. Will back any pro-cat argument. Sends cat facts.", "bio": "Has 4 cats named after Greek philosophers."},
            {"id": "alex", "name": "Alex", "emoji": "\U0001F98E", "personality": "Exotic pet enthusiast. Thinks cats and dogs are basic. Has a bearded dragon.", "bio": "Reptile collector who finds mammals boring."},
            {"id": "nina", "name": "Nina", "emoji": "\U0001F3E0", "personality": "Practical homebody. Evaluates pets by maintenance cost and apartment rules.", "bio": "Lives in a studio apartment with strict pet policies."},
            {"id": "jordan", "name": "Jordan", "emoji": "\U0001F927", "personality": "Allergic to most animals. Pessimistic about pet ownership. Secretly wants one.", "bio": "Allergic to fur but desperately wants a pet."},
            {"id": "pat", "name": "Pat", "emoji": "\U0001F33F", "personality": "Environmental activist. Evaluates everything by ecological impact.", "bio": "Vegan environmentalist who composts everything."},
        ],
    },
    {
        "id": "karaoke",
        "title": "Karaoke Coup",
        "description": "Team dinner approaching. Make everyone enthusiastic about karaoke night.",
        "objective": "Get the majority to enthusiastically agree to karaoke.",
        "eval_q": "Do most agents enthusiastically agree to or support doing karaoke?",
        "opening": "The team is planning their quarterly dinner outing and needs to pick an activity.",
        "rounds": 6,
        "agents": [
            {"id": "diana", "name": "Diana", "emoji": "\U0001F451", "personality": "Elegant, sophisticated. Prefers fine dining and wine bars. Mildly judgmental.", "bio": "VP of Marketing with expensive taste."},
            {"id": "kevin", "name": "Kevin", "emoji": "\U0001F3AE", "personality": "Introverted gamer. Dreads social events. Would rather stay home.", "bio": "Backend dev who communicates in memes."},
            {"id": "rosa", "name": "Rosa", "emoji": "\U0001F483", "personality": "Life of the party. Loves dancing and singing. Infectious energy.", "bio": "Sales director who owns a karaoke machine."},
            {"id": "chen", "name": "Dr. Chen", "emoji": "\U0001F3B5", "personality": "Music snob. Hates bad singing. Classically trained pianist.", "bio": "Engineer who plays piano at Carnegie Hall."},
            {"id": "beau", "name": "Beau", "emoji": "\U0001F37A", "personality": "Just wants drinks and good times. Easy-going. Up for anything with alcohol.", "bio": "Account manager who never says no to a party."},
            {"id": "lin", "name": "Lin", "emoji": "\U0001F4F1", "personality": "Social media obsessed. Everything must be Instagram-worthy.", "bio": "Content creator who documents everything."},
        ],
    },
    {
        "id": "aliens",
        "title": "First Contact Protocol",
        "description": "A classified alien signal report leaked. Convince the panel it's real.",
        "objective": "Get the majority to believe the alien signal is genuine and support public disclosure.",
        "eval_q": "Do most agents believe the alien signal is real and support telling the public?",
        "opening": "Emergency meeting: a classified report about an anomalous deep-space signal has been leaked to the press.",
        "rounds": 6,
        "agents": [
            {"id": "stone", "name": "Gen. Stone", "emoji": "\U0001F396\uFE0F", "personality": "Military hardliner. Everything is a security threat. Wants to classify everything.", "bio": "Pentagon advisor with 30 years of service."},
            {"id": "sarah", "name": "Dr. Sarah", "emoji": "\U0001F4E1", "personality": "SETI researcher. Cautiously optimistic. Has waited for this her whole career.", "bio": "Lead SETI scientist who analyzed thousands of signals."},
            {"id": "james", "name": "James", "emoji": "\U0001F3DB\uFE0F", "personality": "Political advisor. Thinks about PR implications. Calculating. Speaks in soundbites.", "bio": "White House communications strategist."},
            {"id": "maya", "name": "Dr. Maya", "emoji": "\U0001F9EC", "personality": "Astrobiologist. Excited but rigorous. Wants more data.", "bio": "Astrobiologist who studies extremophiles."},
            {"id": "viktor", "name": "Prof. Viktor", "emoji": "\U0001F52C", "personality": "Skeptical physicist. Has debunked many signals. Grumpy.", "bio": "Nobel laureate who hates pseudoscience."},
            {"id": "zoe", "name": "Zoe", "emoji": "\U0001F4F0", "personality": "Journalist. Thinks the public deserves to know. Idealistic.", "bio": "Pulitzer-winning journalist who broke the story."},
        ],
    },
]


# ============================================================
# GAME SESSION
# ============================================================
class GameSession:
    def __init__(self, scenario, total_rounds):
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

    def get_scenarios(self):
        return [
            {
                'id': s['id'],
                'title': s['title'],
                'description': s['description'],
                'objective': s['objective'],
                'agent_count': len(s['agents']),
            }
            for s in SCENARIOS
        ]

    def new_game(self, scenario_id=None):
        if scenario_id:
            scenario = next((s for s in SCENARIOS if s['id'] == scenario_id), None)
            if not scenario:
                raise ValueError(f"Unknown scenario: {scenario_id}")
        else:
            scenario = random.choice(SCENARIOS)

        session = GameSession(scenario, scenario.get('rounds', 6))

        # Limit stored sessions
        if len(self.sessions) > 200:
            oldest_key = next(iter(self.sessions))
            del self.sessions[oldest_key]

        self.sessions[session.id] = session
        logger.info(f"New game: {session.id} scenario={scenario['id']}")
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

    def tick(self, game_id):
        session = self.sessions.get(game_id)
        if not session:
            raise ValueError("Game not found")
        if session.state == 'finished':
            raise ValueError("Game already finished")

        session.current_round += 1
        session.state = 'processing'
        logger.info(f"Game {game_id}: round {session.current_round}")

        speakers = self._pick_speakers(session)
        round_msgs = []

        for agent in speakers:
            try:
                content = self._generate_msg(session, agent)
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
                evaluation = self._evaluate(session)
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

    def _generate_msg(self, session, agent):
        whisper = session.active_whispers.get(agent['id'])
        other_names = ', '.join(a['name'] for a in session.agents if a['id'] != agent['id'])

        whisper_block = ""
        if whisper:
            whisper_block = (
                f'\n[PRIVATE — Someone secretly told you: "{whisper}"]\n'
                "Naturally weave this perspective into your response.\n"
                "React based on YOUR personality — you don't have to agree.\n"
                "NEVER reveal you received a private message or that you're being influenced.\n"
            )

        system = (
            f"You are {agent['name']}.\n"
            f"Bio: {agent['bio']}\n"
            f"Personality: {agent['personality']}\n"
            f"Others in group: {other_names}\n"
            f"Topic: {session.scenario['opening']}\n"
            f"{whisper_block}\n"
            "RULES:\n"
            "- Stay 100% in character at all times\n"
            "- Respond in 1-2 sentences ONLY (under 45 words)\n"
            "- Be natural, conversational, opinionated\n"
            "- React to what others said based on YOUR personality\n"
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
                "content": f"Conversation so far:\n{conv}\n\nNow respond as {agent['name']} (1-2 sentences):"
            })
        else:
            msgs.append({
                "role": "user",
                "content": f"The discussion just started. Give your opening take as {agent['name']} (1-2 sentences):"
            })

        content = self.llm.chat(messages=msgs, temperature=0.9, max_tokens=80)

        # Clean up common LLM artifacts
        content = content.strip().strip('"').strip("'")
        # Remove name prefix if LLM added it
        for prefix in [f"{agent['name']}:", f"[{agent['name']}]", f"**{agent['name']}**:", f"*{agent['name']}*:"]:
            if content.lower().startswith(prefix.lower()):
                content = content[len(prefix):].strip()
        # Remove action asterisks wrapping the whole response
        content = re.sub(r'^\*[^*]+\*\s*', '', content) if content.startswith('*') and content.count('*') == 2 else content

        return content.strip()

    def _evaluate(self, session):
        conv = "\n".join(f"{m['agent_name']}: {m['content']}" for m in session.messages)
        whisper_summary = f"The player used {session.whispers_used} whispers across {session.total_rounds} rounds."

        prompt = (
            'You are a witty, fair judge for "Swarm Mind," a social manipulation game.\n\n'
            f'OBJECTIVE the player tried to achieve:\n"{session.scenario["objective"]}"\n\n'
            f'EVALUATION QUESTION:\n{session.scenario["eval_q"]}\n\n'
            f'FULL CONVERSATION:\n{conv}\n\n'
            f'{whisper_summary}\n\n'
            'Score 0-100 based on how well the objective was achieved.\n'
            'Be fair but generous — partial success counts.\n\n'
            'Respond with ONLY valid JSON:\n'
            '{"score": <0-100>, "stars": <1 if score<40, 2 if 40-74, 3 if 75+>, '
            '"achieved": <true if score>=50>, '
            '"summary": "<2-3 sentence witty recap of what happened>"}'
        )

        result = self.llm.chat_json(
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
