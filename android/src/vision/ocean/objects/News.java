package vision.ocean.objects;

public class News {
    public String id;
    public String author;
    public String title;
    public int time;
    public String description;
    public String imageSource;
    public String link;

    public News(String id, String author, String title, int time, String description, String imageSource, String link) {
        this.id = id;
        this.author = author;
        this.title = title;
        this.time = time;
        this.description = description;
        this.imageSource = imageSource;
        this.link = link;
    }
}
