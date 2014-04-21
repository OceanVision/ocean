package vision.ocean.fragments;

import android.app.Activity;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;

import java.io.UnsupportedEncodingException;
import java.util.ArrayList;

import android.preference.PreferenceManager;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.GridView;
import android.widget.Toast;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import vision.ocean.adapters.NewsAdapter;
import vision.ocean.helpers.MyHttpClient;
import vision.ocean.objects.Feed;
import vision.ocean.objects.News;
import vision.ocean.R;
import vision.ocean.activities.MainActivity;

/**
 * A placeholder fragment containing a simple view.
 */
public class NewsFragment extends Fragment {

    // Web service uri.
    private static final String GET_NEWS_LIST_URI = "http://ocean-coral.no-ip.biz:14/get_article_list";

    /**
     * The fragment argument representing the section number for this
     * fragment.
     */
    private static final String ARG_SECTION_ID = "section_id";
    private static final String ARG_SECTION_TITLE = "section_title";

    private GridView mGridView;
    private NewsAdapter mAdapter;

    /**
     * Returns a new instance of this fragment for the given section
     * number.
     */
    public static NewsFragment newInstance(String feedId, String feedTitle) {
        NewsFragment fragment = new NewsFragment();
        Bundle args = new Bundle();
        args.putString(ARG_SECTION_ID, feedId);
        args.putString(ARG_SECTION_TITLE, feedTitle);
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

        new GetFeedListTask().execute();

        return mGridView;
    }

    @Override
    public void onAttach(Activity activity) {
        super.onAttach(activity);
        ((MainActivity) activity).onSectionAttached(getArguments().getString(ARG_SECTION_TITLE));
    }

    /**
     * Represents an asynchronous get feeds task used to fill navigation drawer with users feeds.
     */
    private class GetFeedListTask extends AsyncTask<Void, Void, JSONObject> {
        SharedPreferences sharedPreferences;

        private GetFeedListTask() {
            this.sharedPreferences = PreferenceManager
                    .getDefaultSharedPreferences(getActivity().getApplicationContext());
        }

        @Override
        protected JSONObject doInBackground(Void... params) {
            HttpPost httpPost = new HttpPost(GET_NEWS_LIST_URI);

            // Set up method parameters in Json
            JSONObject parameters = new JSONObject();
            try {
                parameters.put("last_news_id", "1");
                parameters.put("count", 7);
                parameters.put("feed_id", getArguments().getString(ARG_SECTION_ID));
                parameters.put("client_id", sharedPreferences.getString(getString(R.string.client_id), "-1"));

                StringEntity parametersString = new StringEntity(parameters.toString(), "UTF-8");
                httpPost.setEntity(parametersString);

            } catch (JSONException e) {
                e.printStackTrace();
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            }

            return MyHttpClient.getJSONObject(httpPost);
        }

        @Override
        protected void onPostExecute(final JSONObject newsObject) {
            ArrayList<News> data = new ArrayList<News>();

            try {
                JSONArray newsList = (JSONArray) newsObject.get("article_list");
                // works faster, see 'Use Enhanced For Loop Syntax" at:
                // http://developer.android.com/training/articles/perf-tips.html
                int len = newsList.length();

                // Populate array from json
                for (int i = 0; i < len; i++) {
                    JSONObject jsonObject = newsList.getJSONObject(i);
                    data.add(new News(jsonObject.getString("article_id"),
                            jsonObject.getString("author"),
                            jsonObject.getString("title"),
                            jsonObject.getInt("time"),
                            jsonObject.getString("description"),
                            jsonObject.getString("image_source")));
                }

            } catch (JSONException e) {
                Log.e("JSONException", e.toString());
                e.printStackTrace();
            }

            mAdapter = new NewsAdapter(getActivity(), R.layout.item_news, data);
            mGridView.setAdapter(mAdapter);
        }
    }
}
