def navbar_context(request):
    """导航栏上下文处理器"""
    user_info = request.session.get('info')
    if not user_info:
        return {'nav_info': ''}
    nav_info = dict()
    if user_info:
        nav_info = {
            'username': user_info['name'],
            'id': user_info['id'],
            'type': user_info['type'],
            'icon': f"icon_{str(user_info['id'])}.png"
        }
    return {
        'nav_info': nav_info,
    }
