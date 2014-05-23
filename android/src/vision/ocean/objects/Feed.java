package vision.ocean.objects;

public class Feed {
    public String link;
    public String name;
    public String id;

    public Feed(String link, String name, String id) {
        this.link = link;
        this.name = name;
        this.id = id;
    }

    public Feed(String name, String id) {
        this.name = name;
        this.id = id;
    }

    public Feed(String name) {
        this.name = name;
    }
}
