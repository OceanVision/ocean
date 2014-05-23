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
import android.widget.AdapterView;
import android.widget.GridView;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import vision.ocean.adapters.NewsAdapter;
import vision.ocean.helpers.MyHttpClient;
import vision.ocean.listeners.EndlessScrollListener;
import vision.ocean.objects.News;
import vision.ocean.R;
import vision.ocean.activities.MainActivity;

/**
 * A placeholder fragment containing a simple view.
 */
public class AddTagsFragment extends Fragment {

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        return inflater.inflate(R.layout.fragment_add_tags, container, false);

    }

}
