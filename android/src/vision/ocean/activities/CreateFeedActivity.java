package vision.ocean.activities;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.util.Log;
import android.support.v4.app.FragmentActivity;
import android.view.View;
import android.widget.Toast;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.json.JSONException;
import org.json.JSONObject;
import vision.ocean.R;
import vision.ocean.fragments.AddTagsFragment;
import vision.ocean.helpers.MyHttpClient;

import static vision.ocean.helpers.StaticFunctions.isNetworkOnline;

import java.io.UnsupportedEncodingException;

public class CreateFeedActivity extends FragmentActivity {

    // Web service uri.
    private final static String CREATE_FEED_URI = "http://ocean-coral.no-ip.biz:14/create_feed";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        if (!isNetworkOnline(getApplicationContext()))
            setContentView(R.layout.layout_no_internet_connection);

        else {
            setContentView(R.layout.activity_create_feed);
            getSupportFragmentManager().beginTransaction()
                    .replace(R.id.create_feed_container, new AddTagsFragment())
                    .commit();
        }
    }

    public void refreshActivity(View v) {
        finish();
        startActivity(getIntent());
    }

    public void actionCreateFeed(View v) {
        finish();
    }

    public void actionCancel(View v) {
        finish();
    }

    /**
     * Represents an asynchronous logout task.
     */
    private class CreateFeedTask extends AsyncTask<Void, Void, JSONObject> {
        SharedPreferences sharedPreferences;

        private CreateFeedTask(Context context) {
            this.sharedPreferences = PreferenceManager
                    .getDefaultSharedPreferences(context.getApplicationContext());
        }

        @Override
        protected JSONObject doInBackground(Void... params) {
            HttpPost httpPost = new HttpPost(CREATE_FEED_URI);

            // Set up method parameters in Json
            JSONObject parameters = new JSONObject();
            try {
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
        protected void onPostExecute(final JSONObject result) {
            // Status: true is login succeed
            boolean status = false;
            try {
                status = result.getBoolean("status");

                if (!status) {
                    // User is still logged in
                    Toast.makeText(getApplicationContext(), getResources().getText(R.string.create_feed_error), Toast.LENGTH_LONG).show();
                } else {

                }

            } catch (JSONException e) {
                Log.e("JSONException", e.toString());
                e.printStackTrace();
            } catch (NullPointerException e) {
                Log.e("NullPointerException", e.toString());
                e.printStackTrace();

                Toast.makeText(getApplicationContext(), getResources().getText(R.string.no_server_connection), Toast.LENGTH_LONG).show();
            }

        }
    }
}
