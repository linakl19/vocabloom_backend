from .auth_views import (
    CustomTokenObtainPairView,
    CustomRefreshTokenView,
    LogoutView,
    IsAuthenticatedView,
    RegisterUserView,
)

from .tag_views import (
    TagListCreateView,
    TagDetailView,
)

from .word_views import (
    WordsByTagView,
    WordListCreateView,
    WordDetailView,
)

from .user_example_views import (
    UserExampleCreateView,
    UserExampleListView,
    UserExampleDetailView,
    GenerateWordExampleView,
)

from .audio_views import (
    TextToSpeechView,
)