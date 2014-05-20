package vision.ocean.activities;

import android.app.ActionBar;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.os.AsyncTask;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import vision.ocean.R;
import vision.ocean.helpers.MyHttpClient;
import vision.ocean.objects.News;

import java.io.UnsupportedEncodingException;
import java.util.ArrayList;

public class NewsDetailsActivity extends Activity {

    public final static String NEWS_ID = "vision.ocean.news_id";
    public final static String NEWS_AUTHOR = "vision.ocean.news_author";
    public final static String NEWS_DESCRIPTION = "vision.ocean.news_description";
    public final static String NEWS_TIME = "vision.ocean.news_time";
    public final static String NEWS_TITLE = "vision.ocean.news_title";
    public final static String NEWS_IMAGE_SOURCE = "vision.ocean.image_source";
    public final static String NEWS_LINK = "vision.ocean.news_link";

    // Web service uri.
    private static final String GET_NEWS_DETAILS_URI = "http://ocean-coral.no-ip.biz:14/get_article_details";

    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Intent intent = getIntent();
        getActionBar().setTitle(intent.getStringExtra(NEWS_AUTHOR));

        setContentView(R.layout.activity_news_details);

        ((TextView) findViewById(R.id.textNewsTime)).setText(String.valueOf(intent.getIntExtra(NEWS_TIME, 0)));
        ((TextView) findViewById(R.id.textNewsAuthor)).setText(intent.getStringExtra(NEWS_AUTHOR));
        ((TextView) findViewById(R.id.textNewsTitle)).setText(intent.getStringExtra(NEWS_TITLE));
        ((TextView) findViewById(R.id.textNewsDescription)).setText(intent.getStringExtra(NEWS_DESCRIPTION));

        new GetNewsDetailsTask(this).execute();

        new DownloadImageTask((ImageView) findViewById(R.id.image), intent.getStringExtra(NEWS_IMAGE_SOURCE)).execute();
    }

    /**
     * Represents an asynchronous get feeds task used to fill navigation drawer with users feeds.
     */
    private class GetNewsDetailsTask extends AsyncTask<Void, Void, JSONObject> {
        SharedPreferences sharedPreferences;
        Context context;

        private GetNewsDetailsTask(Context context) {
            this.context = context;
            this.sharedPreferences = PreferenceManager
                    .getDefaultSharedPreferences(context.getApplicationContext());
        }

        @Override
        protected JSONObject doInBackground(Void... params) {
            HttpPost httpPost = new HttpPost(GET_NEWS_DETAILS_URI);

            // Set up method parameters in Json
            JSONObject parameters = new JSONObject();
            try {
                parameters.put("article_id", getIntent().getStringExtra(NEWS_ID));
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
        protected void onPostExecute(final JSONObject newsDetails) {
//            try {
                // TODO: uncomment after webservice fix
//                ((TextView) findViewById(R.id.textNewsDescription))
//                        .setText(((JSONObject) newsDetails.get("article_details")).getString("body"));
//            } catch (JSONException e) {
//                Log.e("JSONException", e.toString());
//                e.printStackTrace();
//            }
        }
    }

    /**
     * Represents an asynchronous get feeds task used to fill navigation drawer with users feeds.
     */
    private class DownloadImageTask extends AsyncTask<Void, Void, Bitmap> {
        ImageView newsImageView;
        String newsImageSource;

        private DownloadImageTask(ImageView newsImageView, String newsImageSource) {
            this.newsImageView = newsImageView;
            this.newsImageSource = newsImageSource;
        }

        @Override
        protected Bitmap doInBackground(Void... params) {
            return MyHttpClient.downloadImage(newsImageSource);
        }

        @Override
        protected void onPostExecute(final Bitmap image) {
            newsImageView.setImageBitmap(image);
        }
    }
}