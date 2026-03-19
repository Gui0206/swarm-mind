/**
 * Locale detection & UI translations.
 *
 * Detects pt-BR from navigator.language (system setting — no permissions needed).
 * Provides a t(key) helper that returns the translated string.
 */
import { computed } from 'vue'

const systemLang = (navigator.language || navigator.userLanguage || 'en').toLowerCase()
const isPtBr = systemLang.startsWith('pt')

const PT = {
  // ── Home ──
  'home.tag': 'Jogo de Agentes LLM',
  'home.title1': 'Sussurre para o enxame.',
  'home.title2': 'Molde a realidade.',
  'home.desc': 'Você é um manipulador invisível em uma sala de agentes de IA. Cada um tem personalidade, opiniões e objetivos únicos. <strong>Sussurre</strong> para qualquer agente para conduzir a conversa e alcançar seu <strong>objetivo secreto</strong> antes que as rodadas acabem.',
  'home.play': 'JOGAR AGORA',
  'home.create': 'CRIE O SEU',
  'home.scenarios': 'Cenários',
  'home.agents': 'Agentes Únicos',
  'home.replayability': 'Rejogabilidade',
  'home.how': 'Como Funciona',
  'home.step1.t': 'Escolha um Cenário',
  'home.step1.d': 'Escolha uma missão com agentes únicos e um objetivo secreto.',
  'home.step2.t': 'Observe & Sussurre',
  'home.step2.d': 'Veja os agentes debaterem, depois sussurre para um para influenciar a conversa.',
  'home.step3.t': 'Molde o Resultado',
  'home.step3.d': 'Cada agente reage com inteligência LLM real. Manipule a mente do enxame.',
  'home.step4.t': 'Seja Julgado',
  'home.step4.d': 'Um juiz de IA avalia o quão bem você alcançou seu objetivo.',
  'home.preview.desc1': 'Convença o escritório inteiro de que pizza de abacaxi é o caminho.',
  'home.preview.desc2': 'Convença a galera do churrasco a colocar Los Hermanos.',

  // ── Lobby ──
  'lobby.tagline': 'Sussurre para o enxame. Molde a realidade.',
  'lobby.desc': 'Você é um manipulador invisível em um grupo de agentes de IA. Cada um tem uma personalidade única. <strong>Sussurre</strong> para qualquer agente para influenciar a conversa e alcançar seu <strong>objetivo secreto</strong> antes que as rodadas acabem.',
  'lobby.custom': 'CENÁRIO CUSTOMIZADO',
  'lobby.play_custom': 'JOGAR ESTE DESAFIO',
  'lobby.initializing': 'INICIALIZANDO ENXAME...',
  'lobby.browse': 'ou veja todos os cenários',
  'lobby.random': 'CENÁRIO ALEATÓRIO',
  'lobby.agents_count': 'agentes',

  // ── Game HUD ──
  'hud.exit': 'SAIR',
  'hud.round': 'RODADA',
  'hud.your_key': 'SUA CHAVE',

  // ── Conversation ──
  'conv.thinking': 'Os agentes estão discutindo...',
  'conv.waiting': 'Esperando os agentes começarem a conversa...',
  'conv.whispered': 'sussurrado',
  'conv.game_over': 'FIM DE JOGO',
  'conv.mission_complete': 'MISSÃO COMPLETA',
  'conv.mission_failed': 'MISSÃO FALHOU',
  'conv.retry': 'TENTAR DE NOVO',
  'conv.all_scenarios': 'TODOS OS CENÁRIOS',
  'conv.rounds': 'rodadas',
  'conv.whispers': 'sussurros',
  'conv.messages': 'mensagens',

  // ── Whisper Panel ──
  'whisper.to': 'SUSSURRAR PARA',
  'whisper.select': 'Selecione um agente...',
  'whisper.placeholder': 'vai ouvir isso...',
  'whisper.placeholder_empty': 'Selecione um agente primeiro, depois escreva seu sussurro...',
  'whisper.send': 'ENVIAR SUSSURRO & CONTINUAR',
  'whisper.skip': 'PULAR & CONTINUAR',

  // ── Sidebar ──
  'sidebar.mission': 'MISSÃO',
  'sidebar.agents': 'AGENTES DO ENXAME',
  'sidebar.whispers_used': 'Sussurros usados',
  'sidebar.messages': 'Mensagens',
  'sidebar.your_whispers': 'SEUS SUSSURROS',
  'sidebar.your_key': 'SUA CHAVE API',
  'sidebar.key_hint': 'Usando seus créditos OpenRouter.',
  'sidebar.disconnect': 'Desconectar',
  'sidebar.share': 'COMPARTILHAR ESTE DESAFIO',
  'sidebar.share_hint': 'Copie o link para compartilhar este cenário.',
  'sidebar.copied': 'COPIADO!',
  'sidebar.copy': 'COPIAR',

  // ── BYOK Modal ──
  'byok.used_up': 'Jogos Grátis Acabaram',
  'byok.quota': 'Cota Excedida',
  'byok.msg_free': 'Você jogou seus 5 jogos grátis! Conecte com OpenRouter para continuar jogando com seus próprios créditos.',
  'byok.msg_quota': 'Wow, viralizamos! Nossa cota grátis acabou. Conecte com OpenRouter para continuar jogando com seus próprios créditos.',
  'byok.connect': 'Conectar com OpenRouter',
  'byok.hint': 'Você será redirecionado para o OpenRouter para autorizar o acesso. Nenhuma senha é compartilhada conosco.',
  'byok.later': 'talvez depois',

  // ── Create ──
  'create.title': 'Crie Seu Cenário',
  'create.sub': 'Crie um desafio personalizado e compartilhe com amigos via link. Sem necessidade de conta.',
  'create.play': 'JOGAR',
}

export function useLocale() {
  const locale = computed(() => isPtBr ? 'pt' : 'en')

  function t(key) {
    if (isPtBr && PT[key]) return PT[key]
    return null // null = use original English inline text
  }

  return { locale, isPtBr, t }
}
