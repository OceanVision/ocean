package vision.ocean.objects;

public class Feed {
    public String link;
    public String title;
    public String id;

    public Feed(String link, String title, String id) {
        this.link = link;
        this.title = title;
        this.id = id;
    }

    public Feed(String title, String id) {
        this.title = title;
        this.id = id;
    }

    public Feed(String title) {
        this.title = title;
    }
}
