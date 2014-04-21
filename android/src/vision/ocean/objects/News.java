package vision.ocean.objects;

public class News {
    public String id;
    public String author;
    public String title;
    public int time;
    public String description;
    public String image;

    public News(String id, String author, String title, int time, String description, String image) {
        this.id = id;
        this.author = author;
        this.title = title;
        this.time = time;
        this.description = description;
        this.image = image;
    }
}
