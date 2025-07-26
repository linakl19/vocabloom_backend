from drf_spectacular.extensions import OpenApiAuthenticationExtension

class CookiesJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'vocabloom.authentication.CookiesJWTAuthentication'
    name = 'CookiesJWTAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'access_token',
            'description': 'JWT access token stored in HTTP-only cookie'
        }