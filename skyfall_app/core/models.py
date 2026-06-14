from django.conf import settings
from django.db import models


class CatalogoBase(models.Model):
    """Base para todo conteúdo do livro. criado_por vazio = item oficial;
    preenchido = conteúdo customizado criado por um jogador."""

    nome = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.CASCADE, related_name="+",
    )

    class Meta:
        abstract = True
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    @property
    def oficial(self):
        return self.criado_por_id is None


class Descritor(CatalogoBase):
    class Meta(CatalogoBase.Meta):
        verbose_name = "Descritor"
        verbose_name_plural = "Descritores"


class Pericia(CatalogoBase):
    ATRIBUTOS = [("FOR", "Força"), ("DES", "Destreza"), ("CON", "Constituição"),
                 ("INT", "Inteligência"), ("SAB", "Sabedoria"), ("CAR", "Carisma")]
    atributo_padrao = models.CharField(max_length=3, choices=ATRIBUTOS, default="INT")

    class Meta(CatalogoBase.Meta):
        verbose_name = "Perícia"
        verbose_name_plural = "Perícias"


class Condicao(CatalogoBase):
    class Meta(CatalogoBase.Meta):
        verbose_name = "Condição"
        verbose_name_plural = "Condições"


class Legado(CatalogoBase):
    texto = models.TextField(blank=True)

    class Meta(CatalogoBase.Meta):
        verbose_name = "Legado"


class Maldicao(CatalogoBase):
    texto = models.TextField(blank=True)

    class Meta(CatalogoBase.Meta):
        verbose_name = "Maldição"
        verbose_name_plural = "Maldições"


class Classe(CatalogoBase):
    texto = models.TextField(blank=True)

    class Meta(CatalogoBase.Meta):
        verbose_name = "Classe"


class Trilha(CatalogoBase):
    texto = models.TextField(blank=True)

    class Meta(CatalogoBase.Meta):
        verbose_name = "Trilha"


class Antecedente(CatalogoBase):
    class Meta(CatalogoBase.Meta):
        verbose_name = "Antecedente"


class Bencao(CatalogoBase):
    class Meta(CatalogoBase.Meta):
        verbose_name = "Bênção"
        verbose_name_plural = "Bênçãos"


class Item(CatalogoBase):
    """Catálogo unificado de itens: armas, armaduras, escudos, equipamentos,
    munição, consumíveis, engenhocas magitech, serviços e transportes."""

    TIPOS = [
        ("arma", "Arma"), ("armadura", "Armadura"), ("escudo", "Escudo"),
        ("equipamento", "Equipamento"), ("municao", "Munição"),
        ("consumivel", "Consumível"), ("magitech", "Engenhoca Magitech"),
        ("servico", "Serviço"), ("transporte", "Transporte"), ("outro", "Outro"),
    ]
    CATEGORIAS_ARMA = [("simples", "Simples"), ("marcial", "Marcial"),
                       ("fogo", "Arma de Fogo"), ("regional", "Regional"), ("", "—")]
    tipo = models.CharField(max_length=20, choices=TIPOS, default="equipamento")
    categoria = models.CharField(max_length=20, blank=True, default="",
                                 help_text="simples/marcial/fogo/regional para armas; leve/pesada para armaduras")
    empunhadura = models.CharField(max_length=12, blank=True, default="",
                                   choices=[("uma_mao", "Uma mão"), ("duas_maos", "Duas mãos"), ("", "—")])
    preco = models.IntegerField(null=True, blank=True, help_text="Preço em Trocados (T$)")
    volume = models.IntegerField(default=0)
    dano = models.CharField(max_length=20, blank=True, default="")
    alcance = models.CharField(max_length=20, blank=True, default="")
    reducao_dano = models.IntegerField(default=0)
    descritores = models.ManyToManyField(Descritor, blank=True, related_name="itens")
    descritores_texto = models.CharField(max_length=255, blank=True, default="",
                                         help_text="Descritores com parâmetros, ex: RECARREGÁVEL (1A)")
    nome_registrado = models.CharField(max_length=160, blank=True, default="",
                                       help_text="Nome de patente (engenhocas magitech)")

    class Meta(CatalogoBase.Meta):
        verbose_name = "Item"
        verbose_name_plural = "Itens"

    @property
    def lista_descritores(self):
        if self.descritores_texto:
            return [d.strip() for d in self.descritores_texto.split(",") if d.strip()]
        return [d.nome for d in self.descritores.all()]


class MaterialEspecial(CatalogoBase):
    efeito_resumo = models.CharField(max_length=120, blank=True, default="")
    aumento_preco = models.IntegerField(default=300)

    class Meta(CatalogoBase.Meta):
        verbose_name = "Material Especial"
        verbose_name_plural = "Materiais Especiais"


class Sinapse(CatalogoBase):
    RARIDADES = [("comum", "Comum"), ("incomum", "Incomum"),
                 ("rara", "Rara"), ("muito_rara", "Muito Rara")]
    raridade = models.CharField(max_length=12, choices=RARIDADES, default="comum")
    multiplicador = models.IntegerField(default=1)

    class Meta(CatalogoBase.Meta):
        verbose_name = "Sinapse"


class Sigilo(CatalogoBase):
    TIPOS = [("prefixo", "Prefixo"), ("sufixo", "Sufixo")]
    EQUIPAMENTOS = [("arma", "Arma"), ("armadura", "Armadura"),
                    ("escudo", "Escudo"), ("vestimenta", "Vestimenta")]
    tipo = models.CharField(max_length=8, choices=TIPOS, default="prefixo")
    grau = models.IntegerField(default=1)
    equipamento = models.CharField(max_length=12, choices=EQUIPAMENTOS, default="arma")
    disparo = models.CharField(max_length=12, blank=True, default="")
    cargas = models.IntegerField(default=2)
    efeito = models.TextField(blank=True)
    imbuindo = models.TextField(blank=True)

    class Meta(CatalogoBase.Meta):
        verbose_name = "Sigilo"


class Magia(CatalogoBase):
    CAMADAS = [("truque", "Truque"), ("superficial", "Camada Superficial"),
               ("rasa", "Camada Rasa"), ("profunda", "Camada Profunda")]
    TIPOS = [("controle", "Controle"), ("ofensivo", "Ofensivo"), ("utilitario", "Utilitário")]
    camada = models.CharField(max_length=12, choices=CAMADAS, default="truque")
    tipo = models.CharField(max_length=12, choices=TIPOS, default="utilitario")
    custo_enfase = models.IntegerField(default=0)
    execucao = models.CharField(max_length=24, blank=True, default="ação")

    class Meta(CatalogoBase.Meta):
        verbose_name = "Magia"
        ordering = ["camada", "nome"]


class Habilidade(CatalogoBase):
    """Habilidades ativáveis de legados, classes, trilhas, maldições etc."""

    FONTES = [("legado", "Legado"), ("maldicao", "Maldição"), ("classe", "Classe"),
              ("trilha", "Trilha"), ("antecedente", "Antecedente"), ("bencao", "Bênção"),
              ("outro", "Outro")]
    custo_enfase = models.IntegerField(default=0)
    execucao = models.CharField(max_length=24, blank=True, default="ação")
    fonte_tipo = models.CharField(max_length=14, choices=FONTES, default="outro")
    fonte_nome = models.CharField(max_length=80, blank=True, default="")

    class Meta(CatalogoBase.Meta):
        verbose_name = "Habilidade"


# ---------------------------------------------------------------- personagem

class Personagem(models.Model):
    TAMANHOS = [("Pequeno", "Pequeno"), ("Médio", "Médio"), ("Médie", "Médie"), ("Grande", "Grande")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="personagens")
    nome = models.CharField(max_length=80)
    pronomes = models.CharField(max_length=40, blank=True, default="")
    jogadore = models.CharField(max_length=80, blank=True, default="")
    nivel = models.IntegerField(default=1)

    classe = models.ForeignKey(Classe, null=True, blank=True, on_delete=models.SET_NULL)
    trilha = models.ForeignKey(Trilha, null=True, blank=True, on_delete=models.SET_NULL)
    legado = models.ForeignKey(Legado, null=True, blank=True, on_delete=models.SET_NULL)
    heranca = models.CharField(max_length=80, blank=True, default="")
    antecedente = models.ForeignKey(Antecedente, null=True, blank=True, on_delete=models.SET_NULL)
    maldicao = models.ForeignKey(Maldicao, null=True, blank=True, on_delete=models.SET_NULL)
    melancolia = models.CharField(max_length=200, blank=True, default="")

    f_for = models.IntegerField("FOR", default=10)
    f_des = models.IntegerField("DES", default=10)
    f_con = models.IntegerField("CON", default=10)
    f_int = models.IntegerField("INT", default=10)
    f_sab = models.IntegerField("SAB", default=10)
    f_car = models.IntegerField("CAR", default=10)

    p_for = models.BooleanField("Proficiência FOR", default=False)
    p_des = models.BooleanField("Proficiência DES", default=False)
    p_con = models.BooleanField("Proficiência CON", default=False)
    p_int = models.BooleanField("Proficiência INT", default=False)
    p_sab = models.BooleanField("Proficiência SAB", default=False)
    p_car = models.BooleanField("Proficiência CAR", default=False)

    pv_maximo = models.IntegerField(default=10)
    pv_atual = models.IntegerField(default=10)
    pv_temporario = models.IntegerField(default=0)
    dados_vida_usados = models.IntegerField(default=0)
    morte_falhas = models.IntegerField(default=0)

    inspiracao = models.BooleanField("Inspiração", default=False)
    catarse = models.IntegerField(default=0)        # máx 5
    enfase_total = models.IntegerField(default=2)
    enfase_atual = models.IntegerField(default=2)
    sombra = models.IntegerField(default=0)

    reducao_dano = models.IntegerField(default=0)
    iniciativa_bonus = models.IntegerField(default=0)
    iniciativa_atual = models.IntegerField(default=0, blank=True)
    tamanho = models.CharField(max_length=12, choices=TAMANHOS, default="Médio")
    deslocamento = models.CharField(max_length=20, default="9 m / 6 q")

    trocados = models.IntegerField(default=0)
    agua = models.IntegerField(default=5, blank=True)
    racoes = models.IntegerField(default=5, blank=True)
    notas_terreno = models.TextField(blank=True, default="")
    condicoes_ativas = models.CharField(max_length=255, blank=True, default="")
    desafio_sucessos = models.IntegerField(default=0, blank=True)
    desafio_falhas = models.IntegerField(default=0, blank=True)

    magias = models.ManyToManyField(Magia, blank=True, related_name="personagens")
    habilidades = models.ManyToManyField(Habilidade, blank=True, related_name="personagens")

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Personagem"
        verbose_name_plural = "Personagens"

    def __str__(self):
        return f"{self.nome} (nv {self.nivel})"

    @property
    def proficiencia(self):
        # bônus de proficiência por nível (2 + nível//4, padrão d20)
        return 2 + (self.nivel - 1) // 4

    def atributo(self, sigla):
        val = getattr(self, f"f_{sigla.lower()}", 10)
        return (val - 10) // 2

    def atributo_valor(self, sigla):
        return getattr(self, f"f_{sigla.lower()}", 10)

    @property
    def atributos(self):
        return {s: self.atributo(s) for s in ["FOR", "DES", "CON", "INT", "SAB", "CAR"]}

    @property
    def protecoes(self):
        return {
            s: 10 + self.atributo(s) + (self.proficiencia if getattr(self, f"p_{s.lower()}") else 0)
            for s in ["FOR", "DES", "CON", "INT", "SAB", "CAR"]
        }

    @property
    def dados_vida_total(self):
        return self.nivel

    @property
    def dado_vida_tipo(self):
        if not self.classe:
            return "d8"
        nome = self.classe.nome.lower()
        if "combatente" in nome:
            return "d10"
        elif "ocultista" in nome:
            return "d6"
        return "d8"

    @property
    def dados_vida_usados_neg(self):
        return -self.dados_vida_usados

    @property
    def limite_volume(self):
        f = self.atributo("FOR")
        tabela = {-3: 10, -2: 12, -1: 14, 0: 16, 1: 19, 2: 22, 3: 25}
        if f in tabela:
            return tabela[f]
        if f < -3:
            return 10
        return max(10, 25 + 3 * (f - 3))

    @property
    def volume_atual(self):
        return sum(
            (e.item.volume or 0) * e.quantidade for e in self.inventario.select_related("item")
        )

    @property
    def limite_fragmentacao(self):
        return self.f_car + self.proficiencia * 2

    @property
    def fragmentacao_atual(self):
        return sum(e.fragmentos for e in self.inventario.all())


class InventarioEntrada(models.Model):
    personagem = models.ForeignKey(Personagem, on_delete=models.CASCADE, related_name="inventario")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="entradas")
    quantidade = models.IntegerField(default=1)
    equipado = models.BooleanField(default=False)
    sigilo_prefixo = models.ForeignKey(Sigilo, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    sigilo_sufixo = models.ForeignKey(Sigilo, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    material = models.ForeignKey(MaterialEspecial, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    fragmentos = models.IntegerField(default=0, help_text="Fragmentos arcanos ocupados pelo item")
    notas = models.CharField(max_length=255, blank=True, default="")
    
    # Novos campos para combate dinâmico
    proficiente = models.BooleanField(default=False)
    atributo_ataque = models.CharField(max_length=3, choices=Pericia.ATRIBUTOS, default="FOR")

    class Meta:
        verbose_name = "Entrada de Inventário"
        verbose_name_plural = "Entradas de Inventário"

    def __str__(self):
        return f"{self.item.nome} x{self.quantidade} ({self.personagem.nome})"

    @property
    def nome_completo(self):
        partes = [self.item.nome]
        if self.material:
            partes.append(f"de {self.material.nome}")
        if self.sigilo_prefixo:
            partes.append(self.sigilo_prefixo.nome.replace("—", "").strip())
        if self.sigilo_sufixo:
            partes.append(self.sigilo_sufixo.nome.replace("—", "").strip())
        return " ".join(partes)


class PericiaPersonagem(models.Model):
    personagem = models.ForeignKey(Personagem, on_delete=models.CASCADE, related_name="pericias")
    pericia = models.ForeignKey(Pericia, on_delete=models.CASCADE, related_name="+")
    atributo = models.CharField(max_length=3, choices=Pericia.ATRIBUTOS, default="INT")
    proficiente = models.BooleanField(default=False)
    expert = models.BooleanField(default=False)

    class Meta:
        unique_together = [("personagem", "pericia")]
        verbose_name = "Perícia do Personagem"
        verbose_name_plural = "Perícias do Personagem"

    def __str__(self):
        return f"{self.pericia.nome} ({self.personagem.nome})"

    @property
    def bonus(self):
        b = self.personagem.atributo(self.atributo)
        if self.expert:
            b += self.personagem.proficiencia * 2
        elif self.proficiente:
            b += self.personagem.proficiencia
        return b
