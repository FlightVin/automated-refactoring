class UserBookTag {
    private String id;
    private String userBookId;
    private String tagId;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getUserBookId() {
        return userBookId;
    }

    public void setUserBookId(String userBookId) {
        this.userBookId = userBookId;
    }

    public String getTagId() {
        return tagId;
    }

    public void setTagId(String tagId) {
        this.tagId = tagId;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((userBookId == null) ? 0 : userBookId.hashCode());
        result = prime * result + ((tagId == null) ? 0 : tagId.hashCode());
        return result;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) {
            return true;
        }
        if (obj == null || getClass() != obj.getClass()) {
            return false;
        }
        UserBookTag other = (UserBookTag) obj;
        return (userBookId == null ? other.userBookId == null : userBookId.equals(other.userBookId))
                && (tagId == null ? other.tagId == null : tagId.equals(other.tagId));
    }

    @Override
    public String toString() {
        return "UserBookTag{" +
                "userBookId='" + userBookId + '\'' +
                ", tagId='" + tagId + '\'' +
                '}';
    }
}