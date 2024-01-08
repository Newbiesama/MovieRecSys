from django.forms import ModelForm


class BootStrapModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段，给每个字段的插件设置
        for name, field in self.fields.items():
            # 若原本没属性，则在原本基础上添加属性
            if field.widget.attrs:
                field.widget.attrs['class'] = "form-control"
                field.widget.attrs['placeholder'] = field.label
            # 若原本没有属性，则直接赋予
            else:
                field.widget.attrs = {'class': "form-control", 'placeholder': field.label}
