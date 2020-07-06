from django.urls import path
from .views import CourseDetailView,CourseListView,LessonDetailView

app_name = "courses"
urlpatterns = [
    path('', CourseListView.as_view(), name="courseList"),
    path('<slug>', CourseDetailView.as_view(), name="courseDetail"),
    path('<course_slug>/<lesson_slug>',LessonDetailView.as_view(), name="lesson-detail")
]
