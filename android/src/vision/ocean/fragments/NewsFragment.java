package vision.ocean.fragments;

import android.app.Activity;
import android.os.Bundle;

import java.util.ArrayList;

import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.GridView;
import vision.ocean.adapters.NewsAdapter;
import vision.ocean.objects.News;
import vision.ocean.R;
import vision.ocean.activities.MainActivity;

/**
 * A placeholder fragment containing a simple view.
 */
public class NewsFragment extends Fragment {
    /**
     * The fragment argument representing the section number for this
     * fragment.
     */
    private static final String ARG_SECTION_NUMBER = "section_number";

    private GridView mGridView;
    private NewsAdapter mAdapter;

    /**
     * Returns a new instance of this fragment for the given section
     * number.
     */
    public static NewsFragment newInstance(int sectionNumber) {
        NewsFragment fragment = new NewsFragment();
        Bundle args = new Bundle();
        args.putInt(ARG_SECTION_NUMBER, sectionNumber);
        fragment.setArguments(args);
        return fragment;
    }

    public NewsFragment() {
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        mGridView = (GridView) inflater.inflate(
                R.layout.fragment_grid_view_news, container, false);

        createGrid();

        return mGridView;
    }

    @Override
    public void onAttach(Activity activity) {
        super.onAttach(activity);
        ((MainActivity) activity).onSectionAttached(getArguments().getInt(ARG_SECTION_NUMBER));
    }

    public void createGrid() {
        String section = Integer.toString(getArguments().getInt(ARG_SECTION_NUMBER));

        ArrayList<News> data = new ArrayList<News>();
        // Populate array from json
        for (int i = 0; i < 5; i++) {
            data.add(new News(section, "Description for this news", R.drawable.ic_launcher));
        }

        mAdapter = new NewsAdapter(getActivity(), R.layout.item_news, data);

        mGridView.setAdapter(mAdapter);
    }
}
