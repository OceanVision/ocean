package vision.ocean.adapters;

import android.app.Activity;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;
import vision.ocean.objects.News;
import vision.ocean.R;

import java.util.ArrayList;

public class NewsAdapter extends ArrayAdapter<News> {

    Context context;
    int layoutResourceId;
    ArrayList data = null;

    public NewsAdapter(Context context, int layoutResourceId, ArrayList<News> data) {
        super(context, layoutResourceId, data);
        this.layoutResourceId = layoutResourceId;
        this.context = context;
        this.data = data;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        NewsHolder holder;

        if (convertView == null) {
            LayoutInflater inflater = ((Activity) context).getLayoutInflater();
            convertView = inflater.inflate(layoutResourceId, parent, false);
            assert convertView != null;

            holder = new NewsHolder();
            holder.title = (TextView) convertView.findViewById(R.id.title);
            holder.description = (TextView) convertView.findViewById(R.id.description);
            holder.image = (ImageView) convertView.findViewById(R.id.image);

            convertView.setTag(holder);
        } else {
            holder = (NewsHolder) convertView.getTag();
        }

        News news = (News) data.get(position);

        holder.title.setText(news.title);
        holder.description.setText(news.description);
        holder.image.setImageResource(news.image);

        return convertView;
    }

    static class NewsHolder {
        TextView title;
        TextView description;
        ImageView image;
    }
}