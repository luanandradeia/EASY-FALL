from django import forms

from . import models


class FormBase(forms.ModelForm):
    """Aplica a classe CSS padrão aos campos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            css = "field"
            if isinstance(f.widget, forms.CheckboxInput):
                css = "check"
            f.widget.attrs.setdefault("class", css)


class PersonagemForm(FormBase):
    class Meta:
        model = models.Personagem
        exclude = ["user", "magias", "habilidades", "criado_em", "atualizado_em"]


class ItemCustomForm(FormBase):
    class Meta:
        model = models.Item
        fields = ["nome", "tipo", "categoria", "empunhadura", "preco", "volume",
                  "dano", "alcance", "reducao_dano", "descritores_texto", "descricao"]


class MagiaCustomForm(FormBase):
    class Meta:
        model = models.Magia
        fields = ["nome", "camada", "tipo", "custo_enfase", "execucao", "descricao"]


class HabilidadeCustomForm(FormBase):
    class Meta:
        model = models.Habilidade
        fields = ["nome", "custo_enfase", "execucao", "fonte_tipo", "fonte_nome", "descricao"]
