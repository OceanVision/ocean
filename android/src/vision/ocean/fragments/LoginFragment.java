package vision.ocean.fragments;

import android.animation.Animator;
import android.animation.AnimatorListenerAdapter;
import android.support.v4.app.Fragment;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.support.v4.app.FragmentActivity;
import android.text.TextUtils;
import android.util.Log;
import android.view.*;
import android.view.inputmethod.EditorInfo;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.json.JSONException;
import org.json.JSONObject;
import vision.ocean.R;
import vision.ocean.helpers.MyHttpClient;

import java.io.UnsupportedEncodingException;

/**
 * Activity which displays a login screen to the user, offering registration as
 * well.
 */
public class LoginFragment extends Fragment {

    // Web service uri.
    private final static String LOGIN_URI = "http://ocean-coral.no-ip.biz:14/sign_in";

    /**
     * Keep track of the login task to ensure we can cancel it if requested.
     */
    private UserLoginTask mAuthTask = null;

    // Login values in moment of login attempt.
    String mUserName;
    String mPassword;

    // UI references.
    private EditText mUserNameView;
    private EditText mPasswordView;
    private View mLoginFormView;
    private View mLoginStatusView;
    private TextView mLoginStatusMessageView;

    public LoginFragment() {
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        View rootView = inflater.inflate(R.layout.fragment_login, container, false);

        // Set up the login form.
        mUserNameView = (EditText) rootView.findViewById(R.id.userName);

        mPasswordView = (EditText) rootView.findViewById(R.id.password);
        mPasswordView
                .setOnEditorActionListener(new TextView.OnEditorActionListener() {
                    @Override
                    public boolean onEditorAction(TextView textView, int id,
                                                  KeyEvent keyEvent) {
                        if (id == R.id.login || id == EditorInfo.IME_NULL) {
                            attemptLogin();
                            return true;
                        }
                        return false;
                    }
                });

        mLoginFormView = rootView.findViewById(R.id.login_form);
        mLoginStatusView = rootView.findViewById(R.id.login_status);
        mLoginStatusMessageView = (TextView) rootView.findViewById(R.id.login_status_message);

        rootView.findViewById(R.id.sign_in_button).setOnClickListener(
                new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        attemptLogin();
                    }
                });

        return rootView;
    }

    /**
     * Attempts to sign in or register the account specified by the login form.
     * If there are form errors (invalid username, missing fields, etc.), the
     * errors are presented and no actual login attempt is made.
     */
    public void attemptLogin() {
        if (mAuthTask != null) {
            return;
        }

        // Reset errors.
        mUserNameView.setError(null);
        mPasswordView.setError(null);

        // Store values at the time of the login attempt.
        mUserName = mUserNameView.getText().toString();
        mPassword = mPasswordView.getText().toString();

        boolean cancel = false;
        View focusView = null;

        // Check for a valid password.
        if (TextUtils.isEmpty(mPassword)) {
            mPasswordView.setError(getString(R.string.error_field_required));
            focusView = mPasswordView;
            cancel = true;
        }

        // Check for a valid username.
        if (TextUtils.isEmpty(mUserName)) {
            mUserNameView.setError(getString(R.string.error_field_required));
            focusView = mUserNameView;
            cancel = true;
        }

        if (cancel) {
            // There was an error; don't attempt login and focus the first
            // form field with an error.
            focusView.requestFocus();
        } else {
            // Show a progress spinner, and kick off a background task to
            // perform the user login attempt.
            mLoginStatusMessageView.setText(R.string.login_progress_signing_in);
            showProgress(true);
            mAuthTask = new UserLoginTask(getActivity());
            mAuthTask.execute((Void) null);
        }
    }

    private void showProgress(final boolean show) {
        /**
         * Application is made only for Android 4.0 and higher
         */
        // On Honeycomb MR2 we have the ViewPropertyAnimator APIs, which allow
        // for very easy animations. If available, use these APIs to fade-in
        // the progress spinner.
        // if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.HONEYCOMB_MR2) {
        int shortAnimTime = getResources().getInteger(
                android.R.integer.config_shortAnimTime);

        mLoginStatusView.setVisibility(View.VISIBLE);
        mLoginStatusView.animate().setDuration(shortAnimTime)
                .alpha(show ? 1 : 0).setListener(new AnimatorListenerAdapter() {
            @Override
            public void onAnimationEnd(Animator animation) {
                mLoginStatusView.setVisibility(show ? View.VISIBLE
                        : View.GONE);
            }
        });

        mLoginFormView.setVisibility(View.VISIBLE);
        mLoginFormView.animate().setDuration(shortAnimTime).alpha(show ? 0 : 1)
                .setListener(new AnimatorListenerAdapter() {
                    @Override
                    public void onAnimationEnd(Animator animation) {
                        mLoginFormView.setVisibility(show ? View.GONE
                                : View.VISIBLE);
                    }
                });
        // } else {
        // // The ViewPropertyAnimator APIs are not available, so simply show
        // // and hide the relevant UI components.
        // mLoginStatusView.setVisibility(show ? View.VISIBLE : View.GONE);
        // mLoginFormView.setVisibility(show ? View.GONE : View.VISIBLE);
        // }
    }

    /**
     * Represents an asynchronous login/registration task used to authenticate
     * the user.
     */
    private class UserLoginTask extends AsyncTask<Void, Void, JSONObject> {
        Context context;
        SharedPreferences sharedPreferences;

        private UserLoginTask(Context context) {
            this.context = context;
            this.sharedPreferences = PreferenceManager
                    .getDefaultSharedPreferences(context.getApplicationContext());
        }

        @Override
        protected JSONObject doInBackground(Void... params) {
            HttpPost httpPost = new HttpPost(LOGIN_URI);

            // Set up method parameters in Json
            JSONObject parameters = new JSONObject();
            try {
                parameters.put("client_id", sharedPreferences.getString(getString(R.string.client_id), "-1"));
                parameters.put("username", mUserName);
                parameters.put("password", mPassword);
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
            mAuthTask = null;
            showProgress(false);

            // Status: true is login succeed
            boolean status = false;
            try {
                status = result.getBoolean("status");

                if (!status) {
                    // Show error if something went wrong
                    mPasswordView
                            .setError(getString(R.string.error_incorrect_password));
                    mPasswordView.requestFocus();

                } else {
                    // User is logged in, update this information in sharedPreferences
                    sharedPreferences.edit().putBoolean(getString(R.string.is_user_authenticated), true).commit();

                    // Refresh mainActivity for logged in user.
                    ((NavigationDrawerFragment) ((FragmentActivity) context).getFragmentManager()
                            .findFragmentById(R.id.navigation_drawer)).setUpDataAdapter();
                    ((FragmentActivity) context).invalidateOptionsMenu();

                    // Go back to refreshed mainActivity
//                ((FragmentActivity) context).getSupportFragmentManager().beginTransaction()
//                        .replace(R.id.container, new Fragment()).commit();
//                ((FragmentActivity) context).getSupportFragmentManager().popBackStack();
                }

            } catch (JSONException e) {
                Log.e("JSONException", e.toString());
                e.printStackTrace();
            } catch (NullPointerException e) {
                Log.e("NullPointerException", e.toString());
                e.printStackTrace();

                Toast.makeText(getActivity(), getResources().getText(R.string.no_server_connection), Toast.LENGTH_LONG).show();
            }


        }

        @Override
        protected void onCancelled() {
            mAuthTask = null;
            showProgress(false);
        }
    }
}
