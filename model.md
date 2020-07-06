# model architecture planning

Membership
    -slug
    -type (free, pro, enterprise)
    -price
    -stripe plan id

usermembership
    -user {foreignkey to default user}
    -stripe customer id
    -membership type {foreignkey to Membership}

Subsription
    -user  membership
    -stripe subscription id
    -active


Course
    -slug
    -title
    -description
    -allowed memebership {foreignKey to Membership}

Lesson
    -slug
    -title
    -course
    -postion
    -video
    -thumbnail