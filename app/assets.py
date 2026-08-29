from flask_assets import Bundle

def compile_static_assets(assets):
    css_bundle = Bundle(
        'css/style.css',
        filters='rcssmin',
        output='gen/packed.css'
    )
    assets.register('css_all', css_bundle)