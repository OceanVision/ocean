package vision.ocean.activities;

import android.app.ActionBar;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.support.v4.widget.DrawerLayout;
import android.support.v4.app.FragmentActivity;
import android.support.v4.app.FragmentManager;
import android.view.View;
import android.widget.Toast;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.json.JSONException;
import org.json.JSONObject;
import vision.ocean.fragments.LoginFragment;
import vision.ocean.fragments.NavigationDrawerFragment;
import vision.ocean.fragments.NewsListFragment;
import vision.ocean.R;
import vision.ocean.helpers.MyHttpClient;
import vision.ocean.objects.News;

import static vision.ocean.helpers.StaticFunctions.isNetworkOnline;

import java.io.UnsupportedEncodingException;

public class MainActivity extends FragmentActivity
        implements NavigationDrawerFragment.NavigationDrawerCallbacks, NewsListFragment.NewsListFragmentCallbacks {

    // Web service uri.
    private final static String LOGOUT_URI = "http://ocean-coral.no-ip.biz:14/sign_out";

    /**
     * Fragment managing the behaviors, interactions and presentation of the navigation drawer.
     */
    private NavigationDrawerFragment mNavigationDrawerFragment;

    /**
     * Used to store the last screen title. For use in {@link #restoreActionBar()}.
     */
    private CharSequence mTitle;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        if (!isNetworkOnline(getApplicationContext()))
            setContentView(R.layout.layout_no_internet_connection);
        else {
            // Check for handshake
            SharedPreferences sharedPreferences = PreferenceManager
                    .getDefaultSharedPreferences(getApplicationContext());

            if (!sharedPreferences.contains(getString(R.string.client_id))) {
                // TODO: handshake
                sharedPreferences.edit().putString(getString(R.string.client_id), "1").commit();
            }

            setContentView(R.layout.activity_main);

            mNavigationDrawerFragment = (NavigationDrawerFragment)
                    getFragmentManager().findFragmentById(R.id.navigation_drawer);
            mTitle = getTitle();

            // Set up the drawer.
            mNavigationDrawerFragment.setUp(
                    R.id.navigation_drawer,
                    (DrawerLayout) findViewById(R.id.drawer_layout));
        }
    }

    @Override
    public void onNavigationDrawerItemSelected(String id, String title) {
        // update the main content by replacing fragments
        FragmentManager fragmentManager = getSupportFragmentManager();

        fragmentManager.beginTransaction()
                .replace(R.id.container, NewsListFragment.newInstance(id, title))
                .commit();
    }

    public void onSectionAttached(String title) {
        mTitle = title;
    }

    public void restoreActionBar() {
        ActionBar actionBar = getActionBar();
        assert actionBar != null;
        actionBar.setNavigationMode(ActionBar.NAVIGATION_MODE_STANDARD);
        actionBar.setDisplayShowTitleEnabled(true);
        actionBar.setTitle(mTitle);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        if (mNavigationDrawerFragment != null && !mNavigationDrawerFragment.isDrawerOpen()) {
            // Only show items in the action bar relevant to this screen
            // if the drawer is not showing. Otherwise, let the drawer
            // decide what to show in the action bar.
            SharedPreferences sharedPreferences = PreferenceManager
                    .getDefaultSharedPreferences(getApplicationContext());

            if (sharedPreferences.getBoolean(getString(R.string.is_user_authenticated), false))
                getMenuInflater().inflate(R.menu.main_authenticated, menu);
            else
                getMenuInflater().inflate(R.menu.main_default, menu);

            restoreActionBar();
            return true;
        }
        return super.onCreateOptionsMenu(menu);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        if (id == R.id.action_settings) {
            return true;

        } else if (id == R.id.action_login) {
            getSupportFragmentManager().beginTransaction()
                    .replace(R.id.container, new LoginFragment()).commit();
            return true;

        } else if (id == R.id.action_logout) {
            new UserLogoutTask(this).execute();
            return true;
        }

        else if (id == R.id.action_create_feed) {
            Intent intent = new Intent(this, CreateFeedActivity.class);
            startActivity(intent);
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @Override
    public void onNewsSelected(News news) {
        Intent intent = new Intent(this, NewsDetailsActivity.class);
        intent.putExtra(NewsDetailsActivity.NEWS_ID, news.id);
        intent.putExtra(NewsDetailsActivity.NEWS_AUTHOR, news.author);
        intent.putExtra(NewsDetailsActivity.NEWS_DESCRIPTION, news.description);
        intent.putExtra(NewsDetailsActivity.NEWS_IMAGE_SOURCE, news.imageSource);
        intent.putExtra(NewsDetailsActivity.NEWS_TIME, news.time);
        intent.putExtra(NewsDetailsActivity.NEWS_TITLE, news.title);
        intent.putExtra(NewsDetailsActivity.NEWS_LINK, news.link);
        startActivity(intent);
    }

    public void refreshActivity(View v) {
        finish();
        startActivity(getIntent());
    }

    /**
     * Represents an asynchronous logout task.
     */
    private class UserLogoutTask extends AsyncTask<Void, Void, JSONObject> {
        Context context;
        SharedPreferences sharedPreferences;

        private UserLogoutTask(Context context) {
            this.context = context;
            this.sharedPreferences = PreferenceManager
                    .getDefaultSharedPreferences(context.getApplicationContext());
        }

        @Override
        protected JSONObject doInBackground(Void... params) {
            HttpPost httpPost = new HttpPost(LOGOUT_URI);

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
                    Toast.makeText(context, getResources().getText(R.string.login_error), Toast.LENGTH_LONG).show();
                } else {
                    // User is logged out, update this information in sharedPreferences
                    sharedPreferences.edit().putBoolean(getString(R.string.is_user_authenticated), false).commit();

                    // Refresh mainActivity for logged out user.
                    ((NavigationDrawerFragment) ((FragmentActivity) context).getFragmentManager()
                            .findFragmentById(R.id.navigation_drawer)).setUpDataAdapter();
                    ((FragmentActivity) context).invalidateOptionsMenu();
                }

            } catch (JSONException e) {
                Log.e("JSONException", e.toString());
                e.printStackTrace();
            } catch (NullPointerException e) {
                Log.e("NullPointerException", e.toString());
                e.printStackTrace();

                Toast.makeText(context, getResources().getText(R.string.no_server_connection), Toast.LENGTH_LONG).show();
            }

        }
    }
}
