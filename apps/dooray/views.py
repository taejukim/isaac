from django.shortcuts import render

# Create your views here.

# GET /project/v1/projects/{project-id}/posts
# size={}                                 /* 기본값 20, 최댓값 100 */
# page={}                                 /* 기본값 0 */
# fromEmailAddress={}                     /* From 이메일 주소로 업무 필터링 */
# fromMemberIds={organizationMemberId}    /* 특정 멤버가 작성한 업무 목록 */
# toMemberIds={organizationMemberId}      /* 특정 멤버가 담당자인 업무 목록 */
# ccMemberIds={organizationMemberId}      /* 특정 멤버가 참조자인 업무 목록 */
# tagIds={tagId}                          /* 특정 태그가 붙은 업무 목록 */
# parentPostId={postId}                   /* 특정 업무의 하위 업무 목록 */
# order={}                                /* postDueAt        만기일 기준 정렬, 역순 정렬은 `-` 를 앞에 붙임 */
#                                         /* postUpdatedAt    업데이트 기준 정렬 */
#                                         /* createdAt        업무 생성일 기준 정렬 */
#                                         /* 역순 정렬은 조건 앞에 `-` 를 붙임, 예) order=-createdAt */

# result[0]['id'] 업무 id
# result[0]['subject']
# result[0]['createAt']
# result[0]['dueDate']
# result[0]['updatedAt']
# result[0]['number'] 업무 번호
# result[0]['users']['to']['type'] 담당자 


# * 서버 
#     * oldap.nhnent.com:389    
# * root DN
#     * ou=NHNENT,o=nhnent.com
# * User search base
#     * ou=Members
# * User search filter
#     * cn={0}
# * Group membership
#     * Search for groups containing user
# * Manager DN
#     * cn=jenkins,o=nhnent.com
# * Manager Password
#     *  jenkins!@#
# *  Display Name LDAP Attribute
#     *  sn
# *  Email Address LDAP Attribute
#     *  mail

# GET /project/v1/projects/{project-id}/posts/{post-id}
