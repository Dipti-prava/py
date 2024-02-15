from django.urls import path

from .view.admin.view import admin_login, create_role, create_resource, create_role_resource_mapping, \
    list_documents_admin, admin_dashboard_counts, get_active_users, get_uploaded_files, \
    get_all_department_file_storage_report, download_all_excel_report, get_departments, get_categories, \
    get_sub_categories, get_all_documents
from .view.department.category import add_category, get_category, get_category_dropdown, update_category, \
    delete_category, add_sub_category, update_sub_category, get_sub_category, delete_sub_category, \
    get_sub_category_dropdown
from .view.department.department import get_departments_by_userid, get_department_file_storage_report, \
    download_excel_report
from .view.department.document import upload_document, list_documents, delete_document, get_document_by_id, \
    get_counts_document, get_documentby_doc_id, update_document
from .view.login_view import signup, signin, logout, captcha_image, send_otp, update_profile, change_password, \
    get_profile_details, create_password, otp_verification
from .views import create_grievance, update_grievance, delete_grievance, view_grievance, view_grievance_by_userid, \
    get_grievances_by_userorgkid

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('captcha/', captcha_image, name='captcha_image'),
    path('sendOTP/', send_otp, name='send_otp'),
    path('otpVerification/', otp_verification, name='otp_verification'),
    path('signin/', signin, name='signin'),
    path('logout/', logout, name='logout'),
    path('grievances/', create_grievance, name='create_grievance'),
    path('grievances/<str:gk_id>/', update_grievance, name='update_grievance'),
    path('delete_grievance/<str:gk_id>/', delete_grievance, name='delete_grievance'),
    path('view/', view_grievance, name='view_grievance'),
    path('viewByUserId/<str:user_id>', view_grievance_by_userid, name='view_grievance_by_userid'),
    path('getDataById/', get_grievances_by_userorgkid, name='get_grievances_by_userorgkid'),

    # =====================Urls for Admin=============================
    path('admin/signin/', admin_login, name='admin_login'),
    path('admin/create_role/', create_role, name='create_role'),
    path('admin/create_resource/', create_resource, name='create_resource'),
    path('admin/role_resource_mapping/', create_role_resource_mapping, name='create_role_resource_mapping'),
    path('admin/list_document/', list_documents_admin, name='list_documents'),
    path('admin/adminDashboardCounts/', admin_dashboard_counts, name='admin_dashboard_counts'),
    path('admin/getActiveUsers/', get_active_users, name='get_active_users'),
    path('admin/getUploadedFiles/', get_uploaded_files, name='get_uploaded_files'),
    path('admin/getDepartmentFileStorageReport/', get_all_department_file_storage_report,
         name='get_department_file_storage_report'),
    path('admin/downloadExcelReport/', download_all_excel_report, name='download_excel_report'),
    path('admin/getAllDepartments/', get_departments, name='get_departments'),
    path('admin/getAllCategory/<str:dep_id>', get_categories, name='get_categories'),
    path('admin/getAllSubCategory/<str:cat_id>', get_sub_categories, name='get_sub_categories'),
    path('admin/getAllDocument/', get_all_documents, name='get_all_documents'),

    # ==================== document upload ============================
    path('department/upload_document/', upload_document, name='upload_document'),
    path('department/getAllDocument/', list_documents, name='list_documents'),
    path('department/delete_document/', delete_document, name='delete_document'),
    path('department/get_document_by_id/', get_document_by_id, name='get_document_by_id'),
    path('department/get_documentby_doc_id/', get_documentby_doc_id, name='get_documentby_doc_id'),
    path('department/update_document/', update_document, name='update_document'),
    path('department/getCounts/', get_counts_document, name='get_counts_document'),
    path('user/getAllDepartments/', get_departments_by_userid, name='get_departments_by_userid'),
    path('user/addCategory/', add_category, name='add_category'),
    path('user/userProfileDetails/', get_profile_details, name='get_profile_details'),
    path('user/updateProfile/', update_profile, name='update_profile'),
    path('user/getCategortTbl/', get_category, name='get_category'),
    path('user/getCategory/', get_category_dropdown, name='get_category_dropdown'),
    path('user/updateCategory/', update_category, name='update_category'),
    path('user/deleteCategory/', delete_category, name="delete_category"),
    path('user/changePassword/', change_password, name="change_password"),
    path('createPassword/', create_password, name='create_password'),
    path('user/getDepartmentFileStorageReport/', get_department_file_storage_report, name="get_department_file_storage_report"),
    path('user/downloadExcelReport/', download_excel_report, name="download_excel_report"),
    path('departments/addSubCategory/', add_sub_category, name="add_sub_category"),
    path('departments/updateSubCategory/', update_sub_category, name="update_sub_category"),
    path('departments/deleteSubCategory/', delete_sub_category, name="delete_sub_category"),
    path('departments/getSubCategoryTbl/', get_sub_category, name='get_sub_category'),
    path('departments/getSubCategory/', get_sub_category_dropdown, name='get_sub_category_dropdown'),

]
