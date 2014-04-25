package vision.ocean.adapters;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.TextView;
import vision.ocean.R;
import vision.ocean.objects.Feed;

import java.util.ArrayList;
import java.util.TreeSet;

public class NavigationDrawerAdapter extends BaseAdapter {

    private static final int TYPE_ITEM = 0;
    private static final int TYPE_SEPARATOR = 1;
    private static final int TYPE_MAX_COUNT = TYPE_SEPARATOR + 1;

    private ArrayList<Feed> mData = new ArrayList<Feed>();
    private LayoutInflater mInflater;

    public TreeSet<Integer> mSeparatorsSet = new TreeSet<Integer>();

    public NavigationDrawerAdapter(Context context) {
        mInflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
    }

    public void addItem(final Feed item) {
        mData.add(item);
        notifyDataSetChanged();
    }

    public void addSeparatorItem(final Feed item) {
        mData.add(item);
        // save separator position
        mSeparatorsSet.add(mData.size() - 1);
        notifyDataSetChanged();
    }

    @Override
    public int getItemViewType(int position) {
        return mSeparatorsSet.contains(position) ? TYPE_SEPARATOR : TYPE_ITEM;
    }

    @Override
    public int getViewTypeCount() {
        return TYPE_MAX_COUNT;
    }

    @Override
    public int getCount() {
        return mData.size();
    }

    @Override
    public Feed getItem(int position) {
        return mData.get(position);
    }

    @Override
    public long getItemId(int position) {
        return position;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder = null;
        int type = getItemViewType(position);

        if (convertView == null) {
            holder = new ViewHolder();
            switch (type) {
                case TYPE_ITEM:
                    convertView = mInflater.inflate(android.R.layout.simple_list_item_activated_1, null);
                    holder.textView = (TextView) convertView.findViewById(android.R.id.text1);
                    break;
                case TYPE_SEPARATOR:
                    convertView = mInflater.inflate(R.layout.item_drawer_separator, null);
                    holder.textView = (TextView) convertView.findViewById(R.id.text_separator);
                    break;
            }
            convertView.setTag(holder);
        } else {
            holder = (ViewHolder) convertView.getTag();
        }

        holder.textView.setText(mData.get(position).title);
        return convertView;
    }

    public static class ViewHolder {
        public TextView textView;
    }
}